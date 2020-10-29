"""
Definition of urls for streaming.
"""

from datetime import datetime
from django.urls import path

from management import views

urlpatterns = [
    path('setup_competition/', views.setup_competition, name='setup_competition'),
    path('setup_judges/<int:id>', views.setup_judges, name='setup_judges'),
    path('setup_athletes/<int:id>', views.setup_athletes, name='setup_athletes'),
    path('setup_cameras/<int:id>', views.setup_cameras, name='setup_cameras'),
    path('setup_sponsors/<int:id>', views.setup_sponsors, name='setup_sponsors'),
    path('setup_finish/<int:id>', views.setup_finish, name='setup_finish'),
    path('judges_get/', views.judges_get, name='judges_get'),
    path('judges_update/', views.judges_update, name='judges_update'),
    path('competition_form/', views.competition_form, name='competition_form'),
    path('competition_list/', views.competition_list, name='competition_list'),
    path('competition_delete/', views.competition_delete, name='competition_delete'),
    path('session_form/', views.session_form, name='session_form'),
    path('session_list/', views.session_list, name='session_list'),
    path('session_delete/', views.session_delete, name='session_delete'),
    path('judge_form/', views.judge_form, name='judge_form'),
    path('team_form/', views.team_form, name='team_form'),
    path('athlete_form/', views.athlete_form, name='athlete_form'),
    path('athlete_list/<int:team_id>', views.athlete_list, name='athlete_list'),
    path('athlete_delete/<int:id>', views.athlete_delete, name='athlete_delete'),
    path('team_list/<int:session_id>', views.team_list, name='team_list'),
    path('team_delete/<int:id>', views.team_delete, name='team_delete'),
    path('create_start_lists/<int:session_id>', views.create_start_lists, name='create_start_lists'),
    path('camera_form/', views.camera_form, name='camera_form'),
    path('camera_list/<int:session_id>', views.camera_list, name='camera_list'),
    path('camera_delete/<int:id>', views.camera_delete, name='camera_delete'),
    path('sponsor_form/', views.sponsor_form, name='sponsor_form'),
    path('sponsor_list/<int:session_id>', views.sponsor_list, name='sponsor_list'),
    path('sponsor_delete/<int:id>', views.sponsor_delete, name='sponsor_delete'),
    path('send_session_emails/<int:session_id>', views.send_session_emails, name='send_session_emails'),
    #path('competition_manage/', views.competition_manage, name='competition_manage'),
    #path('competition_create_update/', views.competition_create_update, name='competition_create_update'),
    #path('session_manage/', views.session_manage, name='session_manage'),
    #path('session_create_update/', views.session_create_update, name='session_create_update'),
    #path('athlete_manage/', views.athlete_manage, name='athlete_manage'),
    #path('athlete_create_update/', views.athlete_create_update, name='athlete_create_update'),
    
]
