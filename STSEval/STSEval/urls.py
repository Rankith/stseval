"""
Definition of urls for STSEval.
"""

from datetime import datetime
from django.conf.urls import url
from django.urls import path
import django.contrib.auth.views
from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView

from app import forms, views

# Uncomment the next lines to enable the admin:
# from django.conf.urls import include
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = [
    # Examples:
    path('', views.home, name='home'),
    path('login/', views.loginview, name='loginview'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path('manage/', views.manage, name='manage'),
    path('admin/', admin.site.urls),
    path('competition_list/', views.competition_list, name='competition_list'),
    path('competition_manage/', views.competition_manage, name='competition_manage'),
    path('competition_create_update/', views.competition_create_update, name='competition_create_update'),
    path('competition_delete/', views.competition_delete, name='competition_delete'),
    path('judges_get/', views.judges_get, name='judges_get'),
    path('judges_update/', views.judges_update, name='judges_update'),
    path('athlete_list/', views.athlete_list, name='athlete_list'),
    path('athlete_manage/', views.athlete_manage, name='athlete_manage'),
    path('athlete_create_update/', views.athlete_create_update, name='athlete_create_update'),
    path('athlete_delete/', views.athlete_delete, name='athlete_delete'),
    path('judge_select/', views.judge_select, name='judge_select'),
    path('d1/', views.d1, name='d1'),
    path('ejudge/', views.ejudge, name='ejudge'),
    path('evideo/', views.evideo, name='evideo'),
    path('twitch_connect/', views.twitch_connect, name='twitch_connect'),
    path('twitch_auth/', views.twitch_auth, name='twitch_auth'),
    path('mark_stream/', views.mark_stream, name='mark_stream'),
    path('deduct/', views.deduct, name='deduct'),
    path('deduction_change/', views.deduction_change, name='deduction_change'),
    path('routine_setup/', views.routine_setup, name='routine_setup'),
    path('routine_start_judging/', views.routine_start_judging, name='routine_start_judging'),
    path('routine_athlete_done/', views.routine_athlete_done, name='routine_athlete_done'),
    path('routine_ejudge_done/', views.routine_ejudge_done, name='routine_ejudge_done'),
    path('routine_get_info/', views.routine_get_info, name='routine_get_info'),
    path('routine_delete/', views.routine_delete, name='routine_delete'),
    path('routine_finished/', views.routine_finished, name='routine_finished'),
    path('routine_set_score/', views.routine_set_score, name='routine_set_score'),
    path('build_dots/', views.build_dots, name='build_dots'),
    path('accountability_report/', views.accountability_report, name='accountability_report'),
    path('get_routines_by_DCE/', views.get_routines_by_DCE, name='get_routines_by_DCE'),
    path('scoreboard/', views.scoreboard, name='scoreboard'),
    path('wowza_broadcast/', views.wowza_broadcast, name='wowza_broadcast'),
    path('wowza_play/', views.wowza_play, name='wowza_play'),
    path('firebase_rtc_consumer/', views.firebase_rtc_consumer, name='firebase_rtc_consumer'),
    path('streaming_send_message/', views.streaming_send_message, name='streaming_send_message'),
    #url(r'^login/$',
    #    django.contrib.auth.views.login,
    #    {
    #        'template_name': 'app/login.html',
    #        'authentication_form': app.forms.BootstrapAuthenticationForm,
    #        'extra_context':
    #        {
    #            'title': 'Log in',
    #            'year': datetime.now().year,
    #        }
    #    },
    #    name='login'),
    #url(r'^logout$',
    #    django.contrib.auth.views.logout,
    #    {
    #        'next_page': '/',
    #    },
    #    name='logout'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
]
