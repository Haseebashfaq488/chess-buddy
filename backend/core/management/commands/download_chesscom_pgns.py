import requests
import os
from django.core.management.base import BaseCommand

HEADERS = {
    'User-Agent': 'PersonalChessBuddy/1.0 (contact: F230761@cfd.nu.edu.pk)',
}

class Command(BaseCommand):   # ← MUST be exactly "Command" (capital C)
    help = 'Download all monthly PGN files from chess.com and save them locally'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Your chess.com username')

    def handle(self, *args, **options):
        username = options['username']
        folder = os.path.join('downloads', 'pgn_chesscom')
        os.makedirs(folder, exist_ok=True)

        # Get list of archives
        archives_url = f"https://api.chess.com/pub/player/{username}/games/archives"
        response = requests.get(archives_url, headers=HEADERS)

        if response.status_code != 200:
            self.stdout.write(self.style.ERROR(f"Failed to get archives: {response.status_code}"))
            return

        archives = response.json().get('archives', [])
        self.stdout.write(self.style.SUCCESS(f"Found {len(archives)} monthly archives. Starting download..."))

        downloaded = 0

        for archive_url in archives:
            parts = archive_url.split('/')
            year = parts[-2]
            month = parts[-1]
            filename = f"pgn_{year}_{month}.pgn"
            filepath = os.path.join(folder, filename)

            pgn_url = archive_url + "/pgn"
            pgn_response = requests.get(pgn_url, headers=HEADERS)

            if pgn_response.status_code != 200:
                self.stdout.write(self.style.WARNING(f"Skipped {filename} (status {pgn_response.status_code})"))
                continue

            content = pgn_response.text
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)

            file_size = len(content)
            downloaded += 1
            self.stdout.write(self.style.SUCCESS(f"Downloaded → {filename} ({file_size} chars)"))

        self.stdout.write(self.style.SUCCESS(f"\nDone! {downloaded} PGN files saved in:\n   backend\\downloads\\pgn_chesscom"))