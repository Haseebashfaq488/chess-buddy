import io
import json
import chess
import chess.engine
import chess.pgn
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Game

ENGINE_PATH = r"C:\Users\BH GMAING\Desktop\stockfish\stockfish-windows-x86-64-avx2.exe"


def get_score(info):
    score_obj = info["score"].white()
    if score_obj.is_mate():
        return score_obj.score(mate_score=100000)
    return score_obj.score()


def get_material(board):
    values = {chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3, chess.ROOK: 5, chess.QUEEN: 9}
    material = 0
    for piece_type in values:
        material += len(board.pieces(piece_type, chess.WHITE)) * values[piece_type]
        material -= len(board.pieces(piece_type, chess.BLACK)) * values[piece_type]
    return material


def get_mobility(board):
    return board.legal_moves.count()


def get_game_phase(board):
    piece_count = len(board.piece_map())
    if piece_count > 24:
        return "opening"
    elif piece_count > 12:
        return "middlegame"
    else:
        return "endgame"


def count_attacked(board):
    count = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece and board.is_attacked_by(not piece.color, square):
            count += 1
    return count


def count_defended(board):
    count = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece and board.is_attacked_by(piece.color, square):
            count += 1
    return count


def king_safety(board):
    king_square = board.king(board.turn)
    if king_square is None:
        return 0
    attackers = len(board.attackers(not board.turn, king_square))
    return -attackers


def pawn_structure_damage(board):
    pawns = board.pieces(chess.PAWN, board.turn)
    files = {}
    damage = 0
    for square in pawns:
        file = chess.square_file(square)
        if file in files:
            damage += 1
        else:
            files[file] = 1
    return damage


class Command(BaseCommand):
    help = "Run weakness feature extraction for a single game"

    def add_arguments(self, parser):
        parser.add_argument('--django_user', type=str, required=True, help='Django username')
        parser.add_argument('--game_id', type=int, required=True, help='ID of the game to analyze')

    def handle(self, *args, **options):
        username = options['django_user']
        game_id = options['game_id']

        try:
            django_user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stderr.write(self.style.ERROR(f"Django user '{username}' not found!"))
            return

        try:
            game = Game.objects.get(id=game_id, user=django_user)
        except Game.DoesNotExist:
            self.stderr.write(self.style.ERROR(f"Game ID {game_id} not found for user {username}!"))
            return

        engine = chess.engine.SimpleEngine.popen_uci(ENGINE_PATH)
        pgn_game = chess.pgn.read_game(io.StringIO(game.pgn))
        board = pgn_game.board()
        features = []

        for ply_index, move in enumerate(pgn_game.mainline_moves()):
            material_before = get_material(board)
            info_before = engine.analyse(board, chess.engine.Limit(depth=18))
            eval_before = get_score(info_before)
            best_move = info_before.get("pv", [None])[0]

            temp_board = board.copy()
            if best_move:
                temp_board.push(best_move)
                best_info = engine.analyse(temp_board, chess.engine.Limit(depth=18))
                best_eval_after = get_score(best_info)
            else:
                best_eval_after = eval_before

            board.push(move)
            material_after = get_material(board)
            info_after = engine.analyse(board, chess.engine.Limit(depth=18))
            eval_after = get_score(info_after)

            if board.turn == chess.BLACK:
                centipawn_loss = best_eval_after - eval_after
            else:
                centipawn_loss = eval_after - best_eval_after
            if centipawn_loss < 0:
                centipawn_loss = 0

            feature = {
                "ply": ply_index,
                "centipawn_loss": centipawn_loss,
                "eval_before": eval_before,
                "eval_after": eval_after,
                "best_eval_after": best_eval_after,
                "material_change": material_after - material_before,
                "hanging_piece_created": count_attacked(board),
                "pieces_attacked_after": count_attacked(board),
                "pieces_defended_after": count_defended(board),
                "king_safety_score": king_safety(board),
                "mobility_score": get_mobility(board),
                "pawn_structure_damage": pawn_structure_damage(board),
                "game_phase": get_game_phase(board)
            }
            features.append(feature)

        engine.quit()

        output_file = f"game_{game_id}_features.json"
        with open(output_file, "w") as f:
            json.dump(features, f, indent=2)

        self.stdout.write(self.style.SUCCESS(f"Weakness features saved to {output_file}"))