# core/serializers.py
from rest_framework import serializers
from .models import Profile, Game, GameAnalysis, WeaknessPattern, UserReflection , PracticeSession
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = '__all__'


class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = [
            'id', 'platform', 'external_id', 'pgn', 'played_at',
            'white', 'black', 'result', 'my_color', 'my_rating',
            'opponent_rating', 'opening_eco', 'opening_name',
            'created_at'
        ]
        read_only_fields = ['created_at', 'opening_eco', 'opening_name']


class GameAnalysisSerializer(serializers.ModelSerializer):
    game = serializers.PrimaryKeyRelatedField(queryset=Game.objects.all())

    class Meta:
        model = GameAnalysis
        fields = ['id', 'game', 'insights', 'voice_notes', 'buddy_advice', 'created_at']
        read_only_fields = ['created_at']


class WeaknessPatternSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeaknessPattern
        fields = '__all__'
        read_only_fields = ['last_seen']
        
# core/serializers.py  ← ADD THESE

class PracticeSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PracticeSession
        fields = '__all__'


class UserReflectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserReflection
        fields = '__all__'