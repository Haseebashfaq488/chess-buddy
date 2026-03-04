import requests
import io
import chess.pgn
from datetime import datetime
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Game

HEADERS = {
    'User-Agent': 'PersonalChessBuddy/1.0 (contact: F230761@cfd.nu.edu.pk)',  # ← CHANGE THIS!
}


class Command(BaseCommand):
    help = 'Import games from chess.com for a given user'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Your chess.com username')
        parser.add_argument('--django_user', type=str, default='admin',
                            help='Django superuser username to assign games to (default: admin)')

    def handle(self, *args, **options):
        chesscom_username = options['username']
        django_username = options['django_user']

        try:
            django_user = User.objects.get(username=django_username)
        except User.DoesNotExist:
            self.stderr.write(self.style.ERROR(f"Django user '{django_username}' not found!"))
            return

        # Step 1: Get list of monthly archives
        archives_url = f"https://api.chess.com/pub/player/{chesscom_username}/games/archives"
        response = requests.get(archives_url , headers= HEADERS)
        if response.status_code != 200:
            self.stderr.write(self.style.ERROR(f"Failed to get archives: {response.status_code}"))
            return

        archives = response.json().get('archives', [])
        self.stdout.write(self.style.SUCCESS(f"Found {len(archives)} monthly archives"))

        imported_count = 0

        for archive_url in archives:
            # Step 2: Get PGN for this month
            pgn_url = archive_url + "/pgn"
            pgn_response = requests.get(pgn_url , headers = HEADERS)
            if pgn_response.status_code != 200:
                self.stdout.write(self.style.WARNING(f"Skipping {archive_url} - status {pgn_response.status_code}"))
                continue

            pgn_text = pgn_response.text
            if not pgn_text.strip():
                continue

            # Step 3: Parse multi-game PGN
            pgn_io = io.StringIO(pgn_text)
            while True:
                game = chess.pgn.read_game(pgn_io)
                if game is None:
                    break

                # Extract metadata
                headers = game.headers
                played_at_str = headers.get("UTCDate", "") + " " + headers.get("UTCTime", "")
                try:
                    played_at = datetime.strptime(played_at_str, "%Y.%m.%d %H:%M:%S")
                except:
                    played_at = datetime.now()  # fallback

                white = headers.get("White", "Unknown")
                black = headers.get("Black", "Unknown")
                result = headers.get("Result", "*")

                # Determine your color and ratings
                my_color = 'white' if white.lower() == chesscom_username.lower() else 'black'
                my_rating = int(headers.get("WhiteElo" if my_color == 'white' else "BlackElo", 0))
                opp_rating = int(headers.get("BlackElo" if my_color == 'white' else "WhiteElo", 0))

                # Basic opening (we'll improve later)
                opening_eco = headers.get("ECO", "")
                opening_name = headers.get("Opening", "")

                # Save to DB (skip if external_id already exists)
                external_id = headers.get("Site", "").split('/')[-1]  # e.g. live/123456

                if Game.objects.filter(external_id=external_id, platform='chess.com').exists():
                    continue  # already imported

                Game.objects.create(
                    user=django_user,
                    platform='chess.com',
                    external_id=external_id,
                    pgn=str(game),  # full PGN string
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

        self.stdout.write(self.style.SUCCESS(f"Import finished! Added {imported_count} new games."))