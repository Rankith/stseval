"""
Definition of urls for streaming.
"""

from datetime import datetime
from django.urls import path

from management import views

urlpatterns = [
    path('setup_competition/', views.setup_competition, name='setup_competition'),
    path('setup_judges/', views.setup_judges, name='setup_judges'),
    path('judges_get/', views.judges_get, name='judges_get'),
    path('judges_update/', views.judges_update, name='judges_update'),
    path('competition_form/', views.competition_form, name='competition_form'),
    path('competition_list/', views.competition_list, name='competition_list'),
    path('competition_delete/', views.competition_delete, name='competition_delete'),
    path('session_form/', views.session_form, name='session_form'),
    path('session_list/', views.session_list, name='session_list'),
    path('session_delete/', views.session_delete, name='session_delete'),
    path('judge_form/', views.judge_form, name='judge_form'),
    path('athlete_list/', views.athlete_list, name='athlete_list'),
    path('athlete_delete/', views.athlete_delete, name='athlete_delete'),
    #path('competition_manage/', views.competition_manage, name='competition_manage'),
    #path('competition_create_update/', views.competition_create_update, name='competition_create_update'),
    #path('session_manage/', views.session_manage, name='session_manage'),
    #path('session_create_update/', views.session_create_update, name='session_create_update'),
    #path('athlete_manage/', views.athlete_manage, name='athlete_manage'),
    #path('athlete_create_update/', views.athlete_create_update, name='athlete_create_update'),
    
]
