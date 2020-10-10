"""
Definition of urls for streaming.
"""

from datetime import datetime
from django.urls import path

from streaming import views

urlpatterns = [
    path('create_camera_stream/', views.create_camera_stream, name='streaming/create_camera_stream'),
    path('get_stream_connection_info/', views.get_stream_connection_info, name='streaming/get_stream_connection_info'),
    path('start_stream/', views.start_stream, name='streaming/start_stream'),
    path('stop_stream/', views.stop_stream, name='streaming/stop_stream'),
    path('get_state/', views.get_state, name='streaming/get_state'),
    path('get_stats/', views.get_stats, name='streaming/get_stats'),
    path('update_stream_status/', views.update_stream_status, name='streaming/update_stream_status'),
    path('camera/', views.camera, name='camera'),
]
