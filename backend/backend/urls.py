# backend/urls.py
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Import all your ViewSets
from core.views import (
    ProfileViewSet,
    GameViewSet,
    GameAnalysisViewSet,
    WeaknessPatternViewSet,
    PracticeSessionViewSet,
    UserReflectionViewSet,
)

router = DefaultRouter()
router.register(r'profiles', ProfileViewSet, basename='profile')
router.register(r'games', GameViewSet, basename='game')
router.register(r'game-analyses', GameAnalysisViewSet, basename='gameanalysis')
router.register(r'weaknesses', WeaknessPatternViewSet, basename='weakness')
router.register(r'practice-sessions', PracticeSessionViewSet, basename='practicesession')
router.register(r'reflections', UserReflectionViewSet, basename='reflection')

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # All API endpoints live under /api/
    path('api/', include(router.urls)),
    
    # You can add more top-level paths later, e.g.:
    # path('api/import/', include('core.urls.import_urls')),  # future batch import
    # path('api/practice/', include('core.urls.practice_urls')),  # future if needed
]