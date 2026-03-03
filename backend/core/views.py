# core/views.py  (or create core/api.py)
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Profile, Game, GameAnalysis, WeaknessPattern
from .serializers import *


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]


class GameViewSet(viewsets.ModelViewSet):
    queryset = Game.objects.all()
    serializer_class = GameSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)


class GameAnalysisViewSet(viewsets.ModelViewSet):
    queryset = GameAnalysis.objects.all()
    serializer_class = GameAnalysisSerializer
    permission_classes = [IsAuthenticated]


class WeaknessPatternViewSet(viewsets.ModelViewSet):
    queryset = WeaknessPattern.objects.all()
    serializer_class = WeaknessPatternSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)
    

# core/views.py  ← ADD THESE CLASSES

class PracticeSessionViewSet(viewsets.ModelViewSet):
    queryset = PracticeSession.objects.all()
    serializer_class = PracticeSessionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)


class UserReflectionViewSet(viewsets.ModelViewSet):
    queryset = UserReflection.objects.all()
    serializer_class = UserReflectionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(practice_session__user=self.request.user)