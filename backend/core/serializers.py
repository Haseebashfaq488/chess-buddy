# core/serializers.py

from rest_framework import serializers
from .models import GameAnalysis, MoveAnalysis


class MoveAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = MoveAnalysis
        fields = [
            'id',
            'ply',
            'move_number',
            'player',
            'is_your_move',
            'san',
            'uci',
            'fen_after',
            'eval_before',
            'eval_after',
            'centipawn_loss',
            'classification',
            'top_engine_moves',
            'themes',
            'short_note',
        ]
        read_only_fields = fields  # all read-only for now (analysis is generated)


class GameAnalysisSerializer(serializers.ModelSerializer):
    move_analyses = MoveAnalysisSerializer(many=True, read_only=True)

    class Meta:
        model = GameAnalysis
        fields = [
            'id',
            'game',
            'accuracy_white_pct',
            'accuracy_black_pct',
            'accuracy_yours_pct',
            'avg_centipawn_loss',
            'avg_cpl_yours',
            'blunder_count',
            'mistake_count',
            'inaccuracy_count',
            'avg_time_per_move_yours_sec',
            'time_pressure_moves',
            'main_weakness_tag',
            'opening_performance',
            'buddy_summary',
            'analyzed_at',
            'engine_depth_used',
            'move_analyses',           # nested moves (optional depth control later)
        ]
        read_only_fields = fields  # analysis is backend-generated