# core/admin.py
from django.contrib import admin
from .models import * 


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'current_rating', 'target_rating', 'preferred_voice')
    search_fields = ('user__username',)
    list_filter = ('current_rating',)


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = (
        'played_at', 'platform', 'white', 'black', 'result',
        'my_color', 'my_rating', 'opponent_rating', 'opening_eco'
    )
    list_filter = ('platform', 'my_color', 'result', 'played_at')
    search_fields = ('white', 'black', 'opening_name', 'opening_eco')
    date_hierarchy = 'played_at'
    readonly_fields = ('created_at',)

    fieldsets = (
        ('Basic Info', {
            'fields': ('platform', 'external_id', 'played_at', 'result')
        }),
        ('Players', {
            'fields': ('white', 'black', 'my_color', 'my_rating', 'opponent_rating')
        }),
        ('Opening & PGN', {
            'fields': ('opening_eco', 'opening_name', 'pgn')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(GameAnalysis)
class GameAnalysisAdmin(admin.ModelAdmin):
    list_display = ('game', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('game__white', 'game__black', 'insights')
    raw_id_fields = ('game',)
    readonly_fields = ('created_at',)

    fieldsets = (
        (None, {
            'fields': ('game',)
        }),
        ('Buddy Insights', {
            'fields': ('insights', 'buddy_advice', 'voice_notes')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(WeaknessPattern)
class WeaknessPatternAdmin(admin.ModelAdmin):
    list_display = ('category', 'description_short', 'frequency', 'severity', 'last_seen')
    list_filter = ('category', 'severity')
    search_fields = ('description', 'category')
    readonly_fields = ('last_seen',)

    def description_short(self, obj):
        return obj.description[:60] + "..." if len(obj.description) > 60 else obj.description
    description_short.short_description = "Description"
    
@admin.register(PracticeSession)
class PracticeSessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'session_type', 'started_at', 'is_active')
    list_filter = ('session_type', 'is_active')

@admin.register(UserReflection)
class UserReflectionAdmin(admin.ModelAdmin):
    list_display = ('move_number', 'practice_session', 'user_thought_short', 'created_at')
    list_filter = ('move_number',)
    search_fields = ('user_thought', 'buddy_response')

    def user_thought_short(self, obj):
        return obj.user_thought[:80] + "..."