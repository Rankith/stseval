"""
Definition of urls for STSEval.
"""

from datetime import datetime
from django.urls import include
from django.urls import path
import django.contrib.auth.views
from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings

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
    path('admin/', admin.site.urls),
    path('judge_select/', views.judge_select, name='judge_select'),
    path('d1/', views.d1, name='d1'),
    path('d2_wag/', views.d2_wag, name='d2_wag'),
    path('view_routine/<int:routine_id>/<int:popup>', views.view_routine, name='view_routine'),
    path('d1_edit_score/<int:routine_id>', views.d1_edit_score, name='d1_edit_score'),
    path('ejudge_select/', views.ejudge_select, name='ejudge_select'),
    path('ejudge/', views.ejudge, name='ejudge'),
    path('evideo/', views.evideo, name='evideo'),
    path('deduct/', views.deduct, name='deduct'),
    path('deduction_change/', views.deduction_change, name='deduction_change'),
    path('routine_setup/', views.routine_setup, name='routine_setup'),
    path('routine_start_judging/', views.routine_start_judging, name='routine_start_judging'),
    path('routine_athlete_done/', views.routine_athlete_done, name='routine_athlete_done'),
    path('routine_ejudge_done/', views.routine_ejudge_done, name='routine_ejudge_done'),
    path('routine_ejudge_set_score/', views.routine_ejudge_set_score, name='routine_ejudge_set_score'),
    path('routine_set_dscore/', views.routine_set_dscore, name='routine_set_dscore'),
    path('set_judge_ready/<int:session_id>', views.set_judge_ready, name='set_judge_ready'),
    path('routine_get_info/', views.routine_get_info, name='routine_get_info'),
    path('routine_delete/', views.routine_delete, name='routine_delete'),
    path('routine_delete_admin/', views.routine_delete_admin, name='routine_delete_admin'),
    path('routine_finished/', views.routine_finished, name='routine_finished'),
    path('routine_set_score/', views.routine_set_score, name='routine_set_score'),
    path('routine_swap_d/', views.routine_swap_d, name='routine_swap_d'),
    path('get_last_routine_status/', views.get_last_routine_status, name='get_last_routine_status'),
    path('build_dots/', views.build_dots, name='build_dots'),
    path('accountability_report/', views.accountability_report, name='accountability_report'),
    path('get_routines_by_SE/', views.get_routines_by_SE, name='get_routines_by_SE'),
    path('get_routines_aa/', views.get_routines_aa, name='get_routines_aa'),
    path('get_team_scores/', views.get_team_scores, name='get_team_scores'),
    path('scoreboard/<str:event_name>', views.scoreboard, name='scoreboard'),
    path('scoreboard/', views.scoreboard, name='scoreboard'),
    path('wowza_broadcast/', views.wowza_broadcast, name='wowza_broadcast'),
    path('wowza_play/', views.wowza_play, name='wowza_play'),
    path('save_video/', views.save_video, name='save_video'),
    path('set_judges_participating/', views.set_judges_participating, name='set_judges_participating'),
    path('athlete_mark_done/<int:athlete_id>', views.athlete_mark_done, name='athlete_mark_done'),
    path('athlete_get_info/<int:athlete_id>', views.athlete_get_info, name='athlete_get_info'),
    path('athlete_get_next/', views.athlete_get_next, name='athlete_get_next'),
    path('athlete_mark_done_get_next/<int:athlete_id>', views.athlete_mark_done_get_next, name='athlete_mark_done_get_next'),
    path('athlete_start_list/<str:event_name>/<int:team_id>', views.athlete_start_list, name='athlete_start_list'),
    path('athlete_start_list_admin/<str:event_name>/', views.athlete_start_list_admin, name='athlete_start_list_admin'),
    path('athlete_start_list_spectate/<str:event_name>', views.athlete_start_list_spectate, name='athlete_start_list_spectate'),
    path('athlete_set_active/<int:sl_id>', views.athlete_set_active, name='athlete_set_active'),
    path('athlete_start_list_swap/<int:sl_id>', views.athlete_start_list_swap, name='athlete_start_list_swap'),
    path('athlete_start_list_swap_do/', views.athlete_start_list_swap_do, name='athlete_start_list_swap_do'),
    path('athlete_start_list_update_order/', views.athlete_start_list_update_order, name='athlete_start_list_update_order'),
    path('athlete_routine_remove/', views.athlete_routine_remove, name='athlete_routine_remove'),
    path('set_floor_timer/', views.set_floor_timer, name='set_floor_timer'),
    path('set_fall/', views.set_fall, name='set_fall'),
    path('set_credit/', views.set_credit, name='set_credit'),
    path('coach/<str:event_name>', views.coach, name='coach'),
    path('coach/', views.coach, name='coach'),
    path('overview/<int:session_id>/<str:event_name>', views.overview, name='overview'),
    path('overview/<int:session_id>', views.overview, name='overview'),
    path('spectator_video/', views.spectator_video, name='spectator_video'),
    path('select_session/', views.select_session, name='select_session'),
    path('video_scoreboard/', views.video_scoreboard, name='video_scoreboard'),
    path('scoreboard_export/<int:session_id>/', views.scoreboard_export, name='scoreboard_export'),
    path('scoreboard_export_get/<int:session_id>/', views.scoreboard_export_get, name='scoreboard_export_get'),
    path('backup_video_upload/<int:session_id>/', views.backup_video_upload, name='backup_video_upload'),
    path('backup_video_list/<int:session_id>/<int:team_restriction>/', views.backup_video_list, name='backup_video_list'),
    path('backup_video_manage/<int:session_id>/', views.backup_video_manage, name='backup_video_manage'),
    path('backup_video_delete/<int:backup_video_id>/', views.backup_video_delete, name='backup_video_delete'),
    path('backup_video_display/<int:backup_video_id>/', views.backup_video_display, name='backup_video_display'),
    path('check_backup_video_exists/', views.check_backup_video_exists, name='check_backup_video_exists'),
    path('check_backup_videos_available/<int:session_id>/<str:event_name>/', views.check_backup_videos_available, name='check_backup_videos_available'),
    path('spectate/<int:session_id>/<str:display_type>/<str:event_name>/', views.spectate, name='spectate'),
    path('spectate/<int:session_id>/<str:display_type>/', views.spectate, name='spectate'),
    path('spectate_splash_start/<int:session_id>/', views.spectate_splash_start, name='spectate_splash_start'),
    path('spectate_splash_end/<int:session_id>/', views.spectate_splash_end, name='spectate_splash_end'),
    path('get_routines_evaluated/<int:session_id>/', views.get_routines_evaluated, name='get_routines_evaluated'),
    path('comp/<int:session_id>/', views.comp, name='comp'),
    path('help/<str:help_screen>/', views.help, name='help'),
    path('reset_athlete_warn/', views.reset_athlete_warn, name='reset_athlete_warn'),
    path('reset_athlete/<int:session_id>/<str:event_name>/', views.reset_athlete, name='reset_athlete'),
    path('session_complete_warn/', views.session_complete_warn, name='session_complete_warn'),
    path('session_mark_complete/<int:session_id>/', views.session_mark_complete, name='session_mark_complete'),
    path('session_disable_test_mode/<int:session_id>/', views.session_disable_test_mode, name='session_disable_test_mode'),
    path('check_all_athletes_done/<int:session_id>/', views.check_all_athletes_done, name='check_all_athletes_done'),
    path('streaming/', include('streaming.urls')),
    path('management/', include('management.urls')),
    path('account/', include('account.urls')),
    path('chat/', include('chat.urls')),
    path('video_tutorials/', views.video_tutorials, name='video_tutorials'),
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
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
