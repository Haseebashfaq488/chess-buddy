# core/models.py

from django.db import models
from django.contrib.auth.models import User
import chess.pgn
import io

# ────────────────────────────────────────────────
# Existing models (keep what you already have)
# ────────────────────────────────────────────────

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    current_rating = models.IntegerField(default=800)
    target_rating = models.IntegerField(default=1500)
    preferred_voice = models.CharField(max_length=50, default="default")
    
    def __str__(self):
        return f"{self.user.username}'s Profile"


class Game(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    PLATFORM_CHOICES = [('chess.com', 'Chess.com'), ('lichess', 'Lichess')]
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    external_id = models.CharField(max_length=100, blank=True, null=True)
    
    pgn = models.TextField(help_text="Full PGN of the game")
    played_at = models.DateTimeField()
    
    white = models.CharField(max_length=100)
    black = models.CharField(max_length=100)
    result = models.CharField(max_length=10)
    
    my_color = models.CharField(max_length=5, choices=[('white', 'White'), ('black', 'Black')])
    my_rating = models.IntegerField(null=True, blank=True)
    opponent_rating = models.IntegerField(null=True, blank=True)
    
    opening_eco = models.CharField(max_length=10, blank=True)
    opening_name = models.CharField(max_length=200, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.played_at.date()} - {self.white} vs {self.black} ({self.result})"

    def get_pgn_game(self):
        return chess.pgn.read_game(io.StringIO(self.pgn))


# ────────────────────────────────────────────────
# New / Updated Analysis Models (phase 1 focus)
# ────────────────────────────────────────────────

class GameAnalysis(models.Model):
    """
    Overall summary statistics for one analyzed game.
    Filled by engine analysis (Stockfish / similar).
    """
    game = models.OneToOneField(Game, on_delete=models.CASCADE, related_name='analysis')
    
    # Accuracy & quality metrics (your side only or both)
    accuracy_white_pct   = models.FloatField(null=True, blank=True, help_text="White's overall accuracy %")
    accuracy_black_pct   = models.FloatField(null=True, blank=True, help_text="Black's overall accuracy %")
    accuracy_yours_pct   = models.FloatField(null=True, blank=True, help_text="Your side accuracy %")
    
    avg_centipawn_loss   = models.FloatField(null=True, blank=True, help_text="Average CPL for the game")
    avg_cpl_yours        = models.FloatField(null=True, blank=True, help_text="Your average CPL")
    
    blunder_count        = models.IntegerField(default=0)
    mistake_count        = models.IntegerField(default=0)
    inaccuracy_count     = models.IntegerField(default=0)
    
    # Time-related (only if [%clk] tags exist in PGN)
    avg_time_per_move_yours_sec = models.FloatField(null=True, blank=True)
    time_pressure_moves         = models.IntegerField(default=0, help_text="Moves where you had <10s and position was critical")
    
    # Short auto-generated tags for quick filtering
    main_weakness_tag    = models.CharField(max_length=80, blank=True, help_text="e.g. 'middlegame tactics', 'time trouble'")
    opening_performance  = models.CharField(max_length=80, blank=True, help_text="e.g. 'solid in Ruy Lopez', 'weak in Sicilian'")
    
    # Text summary the Buddy can speak/read
    buddy_summary        = models.TextField(blank=True)
    
    analyzed_at          = models.DateTimeField(auto_now_add=True)
    engine_depth_used    = models.IntegerField(default=18)
    
    weakness_game_summary = models.TextField(blank=True)
    tactic_game_summary = models.TextField(blank=True)
    decision_game_summary = models.TextField(blank=True)

    meta_coach_summary = models.TextField(blank=True)

    def __str__(self):
        return f"Analysis of {self.game}"


class MoveAnalysis(models.Model):
    """
    Detailed per-move engine evaluation.
    One record per half-move (ply).
    Purely objective — no user input/reflections here.
    """
    game_analysis = models.ForeignKey(GameAnalysis, on_delete=models.CASCADE, related_name='move_analyses')
    
    ply               = models.IntegerField()                      # 0 = white move 1, 1 = black move 1, ...
    move_number       = models.IntegerField()                      # human: 1,1,2,2,...
    player            = models.CharField(max_length=5)             # 'white' or 'black'
    is_your_move      = models.BooleanField()                      # True if this was YOUR color's move
    
    san               = models.CharField(max_length=10)            # e4, Nxf6, O-O
    uci               = models.CharField(max_length=5)             # e2e4, g8f6
    fen_after         = models.CharField(max_length=100)           # position after this move
    
    # Engine scores
    eval_before       = models.FloatField(null=True, blank=True, help_text="Centipawns before move (positive = white advantage)")
    eval_after        = models.FloatField(null=True, blank=True)
    centipawn_loss    = models.FloatField(null=True, blank=True)
    
    # Move quality classification
    CLASS_CHOICES = [
        ('book',       'Book move / theory'),
        ('best',       'Best move'),
        ('excellent',  'Excellent'),
        ('good',       'Good'),
        ('inaccuracy', 'Inaccuracy'),
        ('mistake',    'Mistake'),
        ('blunder',    'Blunder'),
        ('missed_win', 'Missed win'),
    ]
    classification    = models.CharField(max_length=20, choices=CLASS_CHOICES, blank=True)
    
    # Optional: top alternatives (can be empty list)
    top_engine_moves  = models.JSONField(default=list, blank=True,
        help_text='Example: [{"uci":"d2d4","score":0.45,"depth":18}, ...]')

    # Simple auto-detected themes (expandable later)
    themes            = models.JSONField(default=list, blank=True,
        help_text='["development", "pawn_break", "hanging_piece", "fork", "pin", ...]')

    # Short generated note
    short_note        = models.CharField(max_length=120, blank=True)
    
    weakness_model_output = models.JSONField(default=dict, blank=True)
    weakness_confidence = models.FloatField(null=True, blank=True)
    weakness_summary = models.TextField(blank=True)
    
    tactic_model_output = models.JSONField(default=dict, blank=True)
    tactic_confidence = models.FloatField(null=True, blank=True)
    tactic_summary = models.TextField(blank=True)
    
    decision_model_output = models.JSONField(default=dict, blank=True)
    decision_confidence = models.FloatField(null=True, blank=True)
    decision_summary = models.TextField(blank=True)
    
    

    class Meta:
        ordering = ['ply']
        verbose_name_plural = "Move Analyses"

    def __str__(self):
        return f"Move {self.move_number} ({self.player}): {self.san} - {self.classification}"