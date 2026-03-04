# core/views.py

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import GameAnalysis, MoveAnalysis
from .serializers import GameAnalysisSerializer, MoveAnalysisSerializer


class GameAnalysisViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only API for game analyses.
    Future: can add filtering by user, date, accuracy, etc.
    """
    queryset = GameAnalysis.objects.all()
    serializer_class = GameAnalysisSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Only show analyses for games belonging to the logged-in user
        return self.queryset.filter(game__user=self.request.user).select_related('game')


class MoveAnalysisViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only API for individual move details.
    Can be used to show move-by-move breakdown in React.
    """
    queryset = MoveAnalysis.objects.all()
    serializer_class = MoveAnalysisSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Security: only moves from user's own games
        return self.queryset.filter(game_analysis__game__user=self.request.user)