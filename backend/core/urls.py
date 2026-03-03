# core/urls.py   ← create this file in the core/ folder
from django.urls import path
from rest_framework.routers import DefaultRouter

# If you prefer to keep some URLs app-specific (optional for now)
# For the moment we use the main router in backend/urls.py
# But you can move router registration here later if the project grows

# Example of what you could add later (e.g. custom actions)
urlpatterns = [
    # path('custom-action/', SomeCustomView.as_view(), name='custom'),
]