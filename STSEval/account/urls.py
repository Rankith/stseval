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
    path('signup/<str:type>/', views.signup, name='signup'),
    path('login/', views.login_admin, name='login'),
    path('login/<str:type>/', views.login_admin, name='login'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('login_judge/', views.login_judge, name='login_judge'),
    path('login_camera/', views.login_camera, name='login_camera'),
    path('login_coach/', views.login_coach, name='login_coach'),
    path('login_multiple/<str:type>/<str:sub_type>/<int:id>', views.login_multiple, name='login_multiple'),
    path('stripe_webhook/', views.stripe_webhook, name='stripe_webhook'),
    path('stripe_payment_screen/<int:session_id>/<str:type>/<int:qty>', views.stripe_payment_screen, name='stripe_payment_screen'),
    path('payments/', views.payments, name='payments'),
    path('stripe_connect_account/', views.stripe_connect_account, name='stripe_connect_account'),
    path('stripe_goto_dashboard/', views.stripe_goto_dashboard, name='stripe_goto_dashboard'),


]
