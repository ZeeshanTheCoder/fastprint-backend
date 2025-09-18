# userprofiles/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Standard CRUD endpoints
    path('profiles/', views.UserProfileListCreateView.as_view(), name='profile-list-create'),
    path('profiles/<int:pk>/', views.UserProfileDetailView.as_view(), name='profile-detail'),
    
    # Custom endpoints for your React app
    path('save-settings/', views.save_account_settings, name='save-account-settings'),
    path('delete-account/<int:profile_id>/', views.delete_account, name='delete-account'),
]