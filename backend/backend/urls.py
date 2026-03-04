# backend/urls.py
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Import all your ViewSets
from core.views import *

router = DefaultRouter()


router.register(r'game-analyses', GameAnalysisViewSet, basename='gameanalysis')
router.register(r'move-analyses', MoveAnalysisViewSet, basename='moveanalysis')


urlpatterns = [
    path('admin/', admin.site.urls),
    
    # All API endpoints live under /api/
    path('api/', include(router.urls)),
    
    # You can add more top-level paths later, e.g.:
    # path('api/import/', include('core.urls.import_urls')),  # future batch import
    # path('api/practice/', include('core.urls.practice_urls')),  # future if needed
]