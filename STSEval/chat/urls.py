"""
Definition of urls for streaming.
"""

from datetime import datetime
from django.urls import path

from chat import views

urlpatterns = [
    path('send_message/', views.send_message, name='send_message'),
    path('get_eligable_chats/', views.get_eligable_chats, name='get_eligable_chats'),
    
]
