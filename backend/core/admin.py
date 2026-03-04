# core/admin.py

from django.contrib import admin
from django.utils.html import format_html
from .models import Game, GameAnalysis, MoveAnalysis  # make sure Game is imported if needed

# ────────────────────────────────────────────────
# GameAnalysis Admin (with inline moves)
# ────────────────────────────────────────────────






@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = (
        'played_at_formatted',
        'platform',
        'white_vs_black',
        'result',
        'my_color',
        'my_rating_display',
        'opening_eco',
        'has_analysis',
    )
    list_filter = (
        'platform',
        'my_color',
        'result',
        'played_at',
        'opening_eco',
    )
    search_fields = (
        'white',
        'black',
        'opening_name',
        'opening_eco',
        'external_id',
    )
    date_hierarchy = 'played_at'
    readonly_fields = (
        'created_at',
        'external_id',
        'pgn_preview',           # ← move it here (custom method)
    )
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('platform', 'external_id', 'played_at', 'result', 'created_at')
        }),
        ('Players & Ratings', {
            'fields': ('white', 'black', 'my_color', 'my_rating', 'opponent_rating')
        }),
        ('Opening', {
            'fields': ('opening_eco', 'opening_name')
        }),
        ('PGN Preview', {              # ← changed title for clarity
            'fields': ('pgn_preview',),
            'classes': ('collapse',)
        }),
    )
    
    # Custom display methods (unchanged)
    @admin.display(description='Date')
    def played_at_formatted(self, obj):
        return obj.played_at.strftime("%Y-%m-%d %H:%M") if obj.played_at else "-"
    
    @admin.display(description='Game')
    def white_vs_black(self, obj):
        return f"{obj.white} vs {obj.black}"
    
    @admin.display(description='Your Rating')
    def my_rating_display(self, obj):
        return obj.my_rating if obj.my_rating else "-"
    
    @admin.display(description='Analysis Exists')
    def has_analysis(self, obj):
        if hasattr(obj, 'analysis') and obj.analysis:
            return format_html('<span style="color: green;">Yes</span>')
        return format_html('<span style="color: red;">No</span>')
    
    @admin.display(description='PGN Preview (first 200 chars)')
    def pgn_preview(self, obj):
        preview = obj.pgn
        return format_html("<pre style='white-space: pre-wrap;'>{}</pre>", preview)

class MoveAnalysisInline(admin.TabularInline):
    model = MoveAnalysis
    extra = 0
    readonly_fields = (
        'ply', 'move_number', 'player', 'is_your_move',
        'san', 'uci', 'fen_after',
        'eval_before', 'eval_after', 'centipawn_loss',
        'classification', 'top_engine_moves', 'themes', 'short_note',
    )
    can_delete = False
    show_change_link = True
    

@admin.register(GameAnalysis)
class GameAnalysisAdmin(admin.ModelAdmin):
    list_display = (
        'game',
        'analyzed_at',
        'accuracy_yours_pct',
        'avg_cpl_yours',
        'blunder_count',
        'mistake_count',
        'inaccuracy_count',
        'main_weakness_tag',
    )
    list_filter = ('analyzed_at', 'main_weakness_tag')
    search_fields = ('game__white', 'game__black', 'buddy_summary')
    readonly_fields = (
        'analyzed_at', 'engine_depth_used',
        'accuracy_white_pct', 'accuracy_black_pct', 'accuracy_yours_pct',
        'avg_centipawn_loss', 'avg_cpl_yours',
        'blunder_count', 'mistake_count', 'inaccuracy_count',
        'buddy_summary',
    )
    date_hierarchy = 'analyzed_at'

    # Correct inline reference (no quotes!)
    inlines = [MoveAnalysisInline]

    fieldsets = (
        ('Game', {'fields': ('game',)}),
        ('Accuracy', {
            'fields': (
                'accuracy_white_pct', 'accuracy_black_pct', 'accuracy_yours_pct',
                'avg_centipawn_loss', 'avg_cpl_yours',
            )
        }),
        ('Classifications', {
            'fields': ('blunder_count', 'mistake_count', 'inaccuracy_count')
        }),
        ('Time & Tags', {
            'fields': (
                'avg_time_per_move_yours_sec', 'time_pressure_moves',
                'main_weakness_tag', 'opening_performance',
            )
        }),
        ('Buddy Summary', {'fields': ('buddy_summary',)}),
        ('Metadata', {'fields': ('analyzed_at', 'engine_depth_used'), 'classes': ('collapse',)}),
    )

# ────────────────────────────────────────────────
# Inline definition (must come BEFORE it's referenced)
# ────────────────────────────────────────────────




# ────────────────────────────────────────────────
# MoveAnalysis Admin (standalone – no inline here!)
# ────────────────────────────────────────────────

@admin.register(MoveAnalysis)
class MoveAnalysisAdmin(admin.ModelAdmin):
    list_display = (
        'game_analysis',
        'move_number',
        'player',
        'san',
        'classification',
        'centipawn_loss',
        'short_note',
    )
    list_filter = ('classification', 'is_your_move')
    search_fields = ('san', 'short_note', 'game_analysis__game__white')
    readonly_fields = (
        'ply', 'move_number', 'player', 'is_your_move',
        'san', 'uci', 'fen_after',
        'eval_before', 'eval_after', 'centipawn_loss',
        'classification', 'top_engine_moves', 'themes', 'short_note',
    )
    
    fieldsets = (
        ('Move', {
            'fields': ('game_analysis', 'ply', 'move_number', 'player', 'is_your_move', 'san', 'uci')
        }),
        ('Position', {'fields': ('fen_after',)}),
        ('Engine', {
            'fields': ('eval_before', 'eval_after', 'centipawn_loss', 'classification')
        }),
        ('Details', {'fields': ('top_engine_moves', 'themes', 'short_note')}),
    )
    # IMPORTANT: NO inlines here!