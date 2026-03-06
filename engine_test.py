import chess
import chess.engine
import chess.pgn
import os

ENGINE_PATH = r"C:\Users\BH GMAING\Desktop\stockfish\stockfish-windows-x86-64-avx2.exe"
PGN_FOLDER_PATH = r"D:\Chess Buddy\backend\downloads\pgn_chesscom"

def get_score(info):
    score_obj = info["score"].white()
    if score_obj.is_mate():
        return score_obj.score(mate_score=100000)
    return score_obj.score()

def evaluate_all_games():
    engine = chess.engine.SimpleEngine.popen_uci(ENGINE_PATH)

    pgn_files = sorted([
        f for f in os.listdir(PGN_FOLDER_PATH)
        if f.endswith(".pgn")
    ])

    for file_name in pgn_files:
        file_path = os.path.join(PGN_FOLDER_PATH, file_name)
        print(f"\nProcessing file: {file_name}")
        print("=" * 60)

        with open(file_path, encoding="utf-8") as pgn_file:
            while True:
                game = chess.pgn.read_game(pgn_file)
                if game is None:
                    break

                print(f"\nGame: {game.headers.get('White')} vs {game.headers.get('Black')}")
                print(f"Date: {game.headers.get('Date')}")
                print("-" * 50)

                board = game.board()

                for ply_index, move in enumerate(game.mainline_moves()):

                    is_white_move = board.turn

                    info_before = engine.analyse(
                        board,
                        chess.engine.Limit(depth=18)
                    )
                    eval_before = get_score(info_before)

                    best_move = info_before.get("pv", [None])[0]
                    best_move_uci = best_move.uci() if best_move else None

                    temp_board = board.copy()
                    if best_move:
                        temp_board.push(best_move)
                        best_info = engine.analyse(
                            temp_board,
                            chess.engine.Limit(depth=18)
                        )
                        best_eval_after = get_score(best_info)
                    else:
                        best_eval_after = eval_before

                    board.push(move)

                    info_after = engine.analyse(
                        board,
                        chess.engine.Limit(depth=18)
                    )
                    eval_after = get_score(info_after)

                    if is_white_move:
                        centipawn_loss = best_eval_after - eval_after
                    else:
                        centipawn_loss = eval_after - best_eval_after

                    if centipawn_loss < 0:
                        centipawn_loss = 0

                    print(f"Ply: {ply_index}")
                    print(f"Played Move: {move.uci()}")
                    print(f"Best Move: {best_move_uci}")
                    print(f"Eval Before: {eval_before}")
                    print(f"Eval After: {eval_after}")
                    print(f"Best Eval After: {best_eval_after}")
                    print(f"Centipawn Loss: {centipawn_loss}")
                    print("-" * 40)

    engine.quit()

if __name__ == "__main__":
    evaluate_all_games()