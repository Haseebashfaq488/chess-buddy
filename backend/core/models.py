# core/models.py
from django.db import models
from django.contrib.auth.models import User
import chess.pgn  # we'll use this later

class Profile(models.Model):
    """Your personal settings & overall stats"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    current_rating = models.IntegerField(default=800)
    target_rating = models.IntegerField(default=1500)
    preferred_voice = models.CharField(max_length=50, default="default")  # for future voice-over
    
    def __str__(self):
        return f"{self.user.username}'s Profile"

class Game(models.Model):
    """Stores every game you import from chess.com or lichess"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    PLATFORM_CHOICES = [('chess.com', 'Chess.com'), ('lichess', 'Lichess')]
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    external_id = models.CharField(max_length=100, blank=True, null=True)  # game ID from platform
    
    pgn = models.TextField(help_text="Full PGN of the game")
    played_at = models.DateTimeField()
    
    white = models.CharField(max_length=100)
    black = models.CharField(max_length=100)
    result = models.CharField(max_length=10)  # "1-0", "0-1", "1/2-1/2"
    
    my_color = models.CharField(max_length=5, choices=[('white', 'White'), ('black', 'Black')])
    my_rating = models.IntegerField(null=True, blank=True)
    opponent_rating = models.IntegerField(null=True, blank=True)
    
    # Auto-filled from PGN
    opening_eco = models.CharField(max_length=10, blank=True)
    opening_name = models.CharField(max_length=200, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.played_at.date()} - {self.white} vs {self.black} ({self.result})"

    def get_board(self):
        """Helper to parse PGN with python-chess (we'll use this a lot)"""
        game = chess.pgn.read_game(io.StringIO(self.pgn))
        return game

class GameAnalysis(models.Model):
    """Where the Buddy stores insights, weaknesses, and your thinking notes"""
    game = models.OneToOneField(Game, on_delete=models.CASCADE, related_name='analysis')
    
    # JSON field for flexible ML insights
    insights = models.JSONField(default=dict)  
    # Example content:
    # {
    #   "thinking_process": "You missed the counterplay on the queenside",
    #   "weakness_detected": "hanging pieces after time pressure",
    #   "recommended_opening_drill": "Italian Game - 3...Bc5 line"
    # }
    
    voice_notes = models.TextField(blank=True, null=True)  # future: store what you said in voice
    buddy_advice = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

class WeaknessPattern(models.Model):
    """Long-term patterns the Buddy learns about you"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField(max_length=50)  # e.g. "opening", "tactics", "time_pressure", "blunder"
    description = models.TextField()
    frequency = models.IntegerField(default=1)
    last_seen = models.DateTimeField(auto_now=True)
    severity = models.IntegerField(default=1)  # 1-10

    def __str__(self):
        return f"{self.category} - {self.description[:50]}"
    
    
# core/models.py  ← ADD THESE AT THE END

class PracticeSession(models.Model):
    """Live practice or redo session with the Buddy"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.SET_NULL, null=True, blank=True)  # optional (for redoing uploaded games)
    session_type = models.CharField(max_length=20, choices=[
        ('new_practice', 'New Practice Game'),
        ('game_review', 'Redo Uploaded Game'),
    ])
    started_at = models.DateTimeField(auto_now_add=True)
    current_pgn = models.TextField(blank=True)  # live PGN being built
    current_move_number = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Session {self.id} - {self.session_type} ({self.user})"


class UserReflection(models.Model):
    """Where you tell the Buddy what you were thinking (voice → text)"""
    practice_session = models.ForeignKey(PracticeSession, on_delete=models.CASCADE, related_name='reflections')
    move_number = models.IntegerField()                    # e.g. after move 12
    position_fen = models.CharField(max_length=100)        # exact board position (super useful)
    
    user_thought = models.TextField()                      # "I played e4 because I wanted to attack..."
    buddy_response = models.TextField(blank=True, null=True)  # Buddy's reply
    
    voice_transcript = models.TextField(blank=True, null=True)  # raw voice if we want
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['move_number']

    def __str__(self):
        return f"Move {self.move_number} - {self.user_thought[:50]}..."