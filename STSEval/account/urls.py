"""
Definition of urls for streaming.
"""

from datetime import datetime
from django.urls import path
from django.contrib.auth.views import LogoutView
from django.contrib.auth import views as auth_views

from account import views

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_admin, name='login'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('login_judge/', views.login_judge, name='login_judge'),
    path('login_camera/', views.login_camera, name='login_camera'),
    path('login_coach/', views.login_coach, name='login_coach'),


]