# core/management/commands/import_chesscom.py
import os
import io
import chess.pgn
from datetime import datetime
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Game


class Command(BaseCommand):
    help = 'Import games from locally downloaded chess.com PGN files'

    def add_arguments(self, parser):
        parser.add_argument('--django_user', type=str, default='admin',
                            help='Django superuser username to assign games to (default: admin)')
        parser.add_argument('--folder', type=str, default='downloads/pgn_chesscom',
                            help='Folder containing the downloaded .pgn files')

    def handle(self, *args, **options):
        django_username = options['django_user']
        folder_path = options['folder']

        try:
            django_user = User.objects.get(username=django_username)
        except User.DoesNotExist:
            self.stderr.write(self.style.ERROR(f"Django user '{django_username}' not found!"))
            return

        if not os.path.isdir(folder_path):
            self.stderr.write(self.style.ERROR(f"Folder not found: {folder_path}"))
            return

        pgn_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.pgn')]
        if not pgn_files:
            self.stdout.write(self.style.WARNING(f"No .pgn files found in {folder_path}"))
            return

        self.stdout.write(self.style.SUCCESS(f"Found {len(pgn_files)} PGN files in {folder_path}. Starting import..."))

        imported_count = 0

        for filename in pgn_files:
            filepath = os.path.join(folder_path, filename)
            self.stdout.write(f"Processing {filename}...")

            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                pgn_text = f.read()

            if not pgn_text.strip():
                self.stdout.write(self.style.WARNING(f"  → Empty file, skipping"))
                continue

            pgn_io = io.StringIO(pgn_text)
            game_count_this_file = 0

            while True:
                game = chess.pgn.read_game(pgn_io)
                if game is None:
                    break

                game_count_this_file += 1

                headers = game.headers

                # Date & time
                played_at_str = headers.get("UTCDate", "") + " " + headers.get("UTCTime", "")
                try:
                    played_at = datetime.strptime(played_at_str.strip(), "%Y.%m.%d %H:%M:%S")
                except:
                    played_at = datetime.now()

                white = headers.get("White", "Unknown")
                black = headers.get("Black", "Unknown")
                result = headers.get("Result", "*")

                # Assume your username is "chuss-smasher" (change if different)
                my_username = "chuss-smasher"
                my_color = 'white' if white.lower() == my_username.lower() else 'black'
                my_rating = int(headers.get("WhiteElo" if my_color == 'white' else "BlackElo", 0) or 0)
                opp_rating = int(headers.get("BlackElo" if my_color == 'white' else "WhiteElo", 0) or 0)

                opening_eco = headers.get("ECO", "")
                opening_name = headers.get("Opening", "")

                # Unique identifier (Site URL tail or fallback)
                site = headers.get("Site", "")
                external_id = site.split('/')[-1] if site else f"local_{filename}_{game_count_this_file}"

                # Skip if already imported
                if Game.objects.filter(external_id=external_id, platform='chess.com').exists():
                    continue

                Game.objects.create(
                    user=django_user,
                    platform='chess.com',
                    external_id=external_id,
                    pgn=str(game),
                    played_at=played_at,
                    white=white,
                    black=black,
                    result=result,
                    my_color=my_color,
                    my_rating=my_rating,
                    opponent_rating=opp_rating,
                    opening_eco=opening_eco,
                    opening_name=opening_name,
                )
                imported_count += 1

            self.stdout.write(self.style.SUCCESS(f"  → Parsed {game_count_this_file} games from {filename}"))

        self.stdout.write(self.style.SUCCESS(f"\nImport finished! Added {imported_count} new games."))