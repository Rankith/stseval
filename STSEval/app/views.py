"""
Definition of views.
"""

from django.shortcuts import render,redirect
from django.http import HttpRequest,JsonResponse,HttpResponse
from django.template import RequestContext
from datetime import datetime
from django.contrib.auth import authenticate, login
from app.models import Twitch,Routine,EJuryDeduction,BackupVideo,DJuryIndicator
from management.models import Competition,Judge,Athlete,Session,Camera,StartList,Team,Event,Disc,Sponsor,RotationOrder,AthleteLevel,AthleteAge
from app.twitch import TwitchAPI
import app.firebase
from time import time
from decimal import Decimal
from streaming.models import WowzaStream
from django.conf import settings
from binascii import a2b_base64
import distutils.util
import os
from django.contrib.auth.decorators import login_required,user_passes_test
from django.db.models import F, Sum
from apscheduler.schedulers.background import BackgroundScheduler
from .forms import VideoUploadForm
from django.core.files import File
from time import perf_counter 
import csv
import account.views

def valid_login_type(match=None):
    def decorator(func):
        def decorated(request, *args, **kwargs):
            if match in request.session.get('type',''):
                return func(request, *args, **kwargs)
            elif match == 'session' and request.session.get('session',None) != None:
                return func(request, *args, **kwargs)
            else:
                return redirect('/')
        return decorated
    return decorator

def loginview(request):
    if request.method == 'POST':
        login_form = LoginForm(data=request.POST)
        if login_form.is_valid():
            username = login_form.cleaned_data.get('username')
            raw_password = login_form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=raw_password)
            login(request, user)
            return redirect('home')
    else:
        login_form = LoginForm()

    context = {
        'form': login_form,
    }
    return render(request, 'app/login.html', context)

def home(request):
    return render(request,'app/index.html')

def judge_select(request):
    context = {
        'title': 'STS Eval 21 Competition Select',
    }
    return render(request,'app/judge_select.html',context)

@valid_login_type(match='d')
def d1(request):
    event = request.session.get('event')
    session = Session.objects.get(pk=request.session.get('session'))
    judges = Judge.objects.filter(session=session,event__name=event)
    athletes = Athlete.objects.filter(team__session=session)
    disc = session.competition.disc.name
    layout = 'app/layout.html'
    type = request.session.get('type')
    if 'd2' in type:
        judge_type = "D2"
        this_judge = judges[0].d2 
    else:
        judge_type = "D1"
        this_judge = judges[0].d1

    if judges[0].d2_email != '':
        #check if dumb wag bullshit
        if session.competition.disc.name == "WAG" and (session.level == Session.WDP or session.level == Session.NCAA): #d2_wag version
            multi_d = False
        else:
            multi_d = True
    else:
        multi_d = False

    simple_d = False

    if disc == "WAG":
        if session.level == Session.WDP or session.level == Session.NCAA:
            #check if its a no E and limited D type of event
            simple_d = True

    
    context = {
        'title':  judge_type + ' Overview - ' + event + ' ' + session.full_name(),
        'judges':judges[0],
        'athletes':athletes,
        'disc':disc,
        'event':event,
        'session':session,
        'loadroutine':'',
        'layout':layout,
        'scoreboard':True,
        'judge_type':judge_type,
        'this_judge':this_judge,
        'multi_d':multi_d,
        'simple_d':simple_d,
        'help':'djudge',

    }
    return render(request,'app/d1.html',context)

def view_routine(request,routine_id,popup):
    routine = Routine.objects.get(pk=routine_id)
    event = routine.event.name
    session_id = routine.session.id
    judges = Judge.objects.filter(session_id=session_id,event=routine.event)
    athletes = Athlete.objects.filter(team__session_id=session_id)
    session = routine.session
    if routine.video_file.name == None or routine.video_file.name == '': #just a check for old stuff
        video_file='/media/routine_videos/' + str(routine.id)
    else:
        video_file=os.path.splitext(routine.video_file.url)[0]
    if popup == 1:
        layout = 'app/layout_empty.html'
    else:
        layout = 'app/layout.html'
    editable = False
    if 'd1' in request.session.get('type') or ('d2' in request.session.get('type') and session.competition.disc.name != 'WAG'):#d1 can edit if its their event
        if request.session.get('event','').lower() == event.lower():
            editable = True
    elif 'admin' in request.session.get('type'):#admin can always edit
        editable = True

    simple_d = False

    if session.competition.disc.name == "WAG":
        if session.level == Session.WDP or session.level == Session.NCAA:
            #check if its a no E and limited D type of event
            simple_d = True

    routine = routine.id
    context = {
        'title': 'D1 Overview - ' + event + ' ' + session.full_name(),
        'judges':judges[0],
        'athletes':athletes,
        'event':event,
        'session':session,
        'loadroutine':routine,
        'layout':layout,
        'editable':editable,
        'video_file':video_file,
        'simple_d':simple_d,
        'multi_d':False,
    }
    return render(request,'app/d1.html',context)

def d1_edit_score(request,routine_id):
    routine = Routine.objects.get(pk=routine_id)
    event = routine.event
    loadroutine = ''
    if 'd1' in request.session.get('type'):#d1 can edit if its their event
        if request.session.get('event','').lower() == event.name.lower():
            loadroutine = routine
    elif 'admin' in request.session.get('type'):#admin can always edit
        loadroutine = routine

    session = routine.session
    if session.competition.disc.name == "WAG" and (session.level == Session.WDP or session.level == Session.NCAA):
        simple_d = True
    else:
        simple_d = False
    context = {
        'loadroutine':routine,
        'simple_d':simple_d,
    }
    return render(request,'app/d1_edit_score.html',context)

def routine_setup(request):
    #athlete = Athlete.objects.get(pk=request.POST.get('athlete'))
    session = Session.objects.get(pk=request.session.get('session'))
    sl = athlete_get_next_do(request.session.get('event'),session.id)
    if sl != None:
    #check for camera
        athlete = sl.athlete
        camera = Camera.objects.filter(teams=athlete.team,events__name=request.session.get('event')).first()
        if camera == None:
            resp = {'routine':-1,
                     'error':'No Camera for ' + athlete.team.name + ' on ' + request.session.get('event') + '.  Contact your Meet Administrator'}
            return JsonResponse(resp)
        #check if its first of this rotation and hard set to D1
        if sl == StartList.objects.filter(session_id=session.id,event__name=request.session.get('event'),active=True,athlete__rotation=sl.athlete.rotation).order_by('order').first():
            djudge = 'D1'
        else:
            djudge = request.POST.get('djudge','D1')
        app.firebase.routine_setup(session,request.session.get('event'),athlete,camera.id,djudge)
        check_update_camera_event(camera.session.id,camera)
        return HttpResponse(status=200)
    else:
        app.firebase.routine_all_done(session,request.session.get('event'))
        check_update_camera_event(session.id)
        return HttpResponse("event done")

def routine_swap_d(request):
    #update this routine and check if it should swap
    routine = Routine.objects.get(pk=request.POST.get('routine'))
    sl = StartList.objects.filter(session=routine.session,event=routine.event,athlete=routine.athlete).first()
    sl.secondary_judging=True
    sl.save()

    sl = athlete_get_next_do(routine.event.name,routine.session.id)
    if sl != None:
        next_rotation = sl.athlete.rotation
    else:
        next_rotation = ''
    judges = Judge.objects.filter(session=routine.session,event=routine.event).first()
    if judges.d2_email != '' and next_rotation == routine.athlete.rotation:
        #d2 was filled out and this wasnt last gymnast in rotation, swap d judges
        if routine.d_judge == 'D1':
            next_judge = 'D2'
        else:
            next_judge = 'D1'
        camera = Camera.objects.filter(teams=sl.athlete.team,events=routine.event).first()
        app.firebase.routine_setup(routine.session,routine.event.name,sl.athlete,camera.id,next_judge)
        app.firebase.routine_set_status(routine.session.id,routine.event.name,routine)
        #check_update_camera_event(camera.session.id,camera)

    return HttpResponse(status=200)

def routine_start_judging(request):
    session = Session.objects.get(pk=request.session.get('session'))
    event = Event.objects.filter(name=request.session.get('event'),disc=session.competition.disc).first()
    routine = Routine(session_id=request.session.get('session'),disc=request.session.get('disc'),event=event,athlete_id=request.POST.get('athlete'),d_judge=request.POST.get('djudge','D1'))
    judges = Judge.objects.filter(session_id=request.session.get('session'),event__name=request.session.get('event')).first()
    routine.e1_name = judges.e1
    routine.e2_name = judges.e2
    routine.e3_name = judges.e3
    routine.e4_name = judges.e4
    routine.d1_name = judges.d1
    #routine = Routine.objects.filter(session_id=request.session.get('session'),disc=request.session.get('disc'),event=request.session.get('event')).order_by('-id').first()
    routine.status = Routine.STARTED
    routine.athlete_id=request.POST.get('athlete')
    if request.POST.get('backup_video') != '-1' and request.POST.get('backup_video') != -1:
        routine.video_from_backup = True

    mili = int(time() * 1000)
    routine.start_time = mili

    routine.save()
    app.firebase.routine_set_status(str(request.session.get('session')),request.session.get('event'),routine)
    app.firebase.update_spectator_feed(str(request.session.get('session')),request.session.get('event'),'routine_start',request.POST.get('athlete'))

    resp = {'routine':routine.id}
    return JsonResponse(resp)

def routine_athlete_done(request):
    routine = Routine.objects.filter(session_id=request.session.get('session'),disc=request.session.get('disc'),event__name=request.session.get('event')).order_by('-id').first()
    routine.status = Routine.ATHLETE_DONE

    #try:
        #api = TwitchAPI()
        #position,vid_id = api.mark_stream('Routine ' + str(routine.id) + ' end')
   # except:
        #position = 0
        #vid_id = 0

    mili = int(time() * 1000)
    routine.athlete_done_time = mili

    routine.save()
    app.firebase.routine_set_status(str(request.session.get('session')) ,request.session.get('event'),routine)
    app.firebase.clear_e_ping(str(request.session.get('session')) ,request.session.get('event'))

    return JsonResponse(Routine.objects.values().get(pk=routine.id),safe=False)

def routine_ejudge_done(request):
    routine = Routine.objects.get(pk=request.POST.get('routine'))
    judge = int(request.POST.get('judge'))
    if judge==1:
        routine.e1_done = True
    elif judge==2:
        routine.e2_done = True
    elif judge==3:
        routine.e3_done = True
    elif judge==4:
        routine.e4_done = True

    routine.save()
    app.firebase.routine_set_ejudge_done(str(routine.session.id),routine.event.name,judge,True)

    return HttpResponse(status=200)

def routine_ejudge_set_score(request):
    routine = Routine.objects.get(pk=request.POST.get('routine'))
    judge = int(request.POST.get('judge'))
    if judge==1:
        routine.e1_done = True
        try:
            routine.score_e1 = round(float(request.POST.get('score',0)),3)
        except:
            routine.score_e1 = 0
    elif judge==2:
        routine.e2_done = True
        try:
            routine.score_e2 = round(float(request.POST.get('score',0)),3)
        except:
            routine.score_e2 = 0
    elif judge==3:
        routine.e3_done = True
        try:
            routine.score_e3 = round(float(request.POST.get('score',0)),3)
        except:
            routine.score_e3 = 0
    elif judge==4:
        routine.e4_done = True
        try:
            routine.score_e4 = round(float(request.POST.get('score',0)),3)
        except:
            routine.score_e4 = 0

    routine.save()
    app.firebase.routine_set_ejudge_done(str(routine.session.id),routine.event.name,judge,True)

    return HttpResponse(status=200)

def routine_d2_set_score(request):
    routine = Routine.objects.get(pk=request.POST.get('routine'))
    try:
        routine.score_final_d2 = round(float(request.POST.get('score',0)),3)
    except:
        routine.score_final_d2 = 0

    routine.save()
    app.firebase.routine_set_d2_score(str(routine.session.id),routine.event.name,routine.score_final_d2)

    return HttpResponse(status=200)

def routine_delete(request):
    routine = Routine.objects.get(pk=request.POST.get('routine'))
    routine.status = Routine.DELETED

    routine.save()

    if os.path.exists(settings.MEDIA_ROOT + '/routine_videos/' + str(routine.session.id) + '/' + routine.event.name + '/' + routine.athlete.name.replace(" ","") + "_" + str(routine.id) + '.webm'):
        os.remove(settings.MEDIA_ROOT + '/routine_videos/' + str(routine.session.id) + '/' + routine.event.name + '/' + routine.athlete.name.replace(" ","") + "_" + str(routine.id) + '.webm')

    app.firebase.routine_set_status(str(routine.session.id),routine.event.name,routine)
    app.firebase.clear_e_ping(str(routine.session.id),routine.event.name)
    

    return HttpResponse(status=200)

def routine_finished(request):
    routine = Routine.objects.get(pk=request.POST.get('routine'))
    routine.status = Routine.FINISHED
    routine.e1_done = True
    routine.e2_done = True
    routine.e3_done = True
    routine.e4_done = True
    mili = int(time() * 1000)
    routine.d1_done_time = mili
    if routine.video_from_backup:
        routine.video_saved = True
        routine.video_converted = True
        bv = BackupVideo.objects.filter(session=routine.session,athlete=routine.athlete,event=routine.event).first()
        if bv != None:
            routine.video_file.name = bv.video_file.name
            bv.reviewed = True
            bv.save()
    
    routine.save()
    app.firebase.routine_set_status(str(routine.session.id) ,routine.event.name,routine)
    app.firebase.update_spectator_feed(str(routine.session.id),routine.event.name,'routine_finished',routine.athlete.id,"{:.1f}".format(routine.score_final))
    #camera = Camera.objects.filter(teams=routine.athlete.team,events__name=routine.event.name).first()
    #check_update_camera_event(routine.session.id,camera)

    return HttpResponse(status=200)

def routine_set_score(request):
    routine = Routine.objects.get(pk=request.POST.get('routine'))
    if request.POST.get('just_edit','') != '':
        routine.status = Routine.REVIEW_DONE
    try:
        routine.score_elements = int(request.POST.get('score_elements'))
    except:
        routine.score_elements = 0
    try:
        routine.score_difficulty = round(float(request.POST.get('score_difficulty')),2)
    except:
        routine.score_difficulty = 0
    try:
        routine.score_groups = round(float(request.POST.get('score_groups')),2)
    except:
        routine.score_groups = 0
    try:
        routine.score_bonus = round(float(request.POST.get('score_bonus')),2)
    except:
        routine.score_bonus = 0
    try:
        routine.score_connection = round(float(request.POST.get('score_connection')),2)
    except:
        routine.score_connection = 0
    try:
        routine.score_neutral = round(float(request.POST.get('score_neutral')),2)
    except:
        routine.score_neutral = 0
    try:
        routine.score_e1 = round(float(request.POST.get('score_e1',0)),2)
    except:
        routine.score_e1 = 0
    try:
        routine.score_e2 = round(float(request.POST.get('score_e2',0)),2)
    except:
        routine.score_e2 = 0
    try:
        routine.score_e3 = round(float(request.POST.get('score_e3',0)),2)
    except:
        routine.score_e3 = 0
    try:
        routine.score_e4 = round(float(request.POST.get('score_e4',0)),2)
    except:
        routine.score_e4 = 0
    try:
        routine.score_e = round(float(request.POST.get('score_e',0)),2)
    except:
        routine.score_e = 0
    try:
        routine.score_d = round(float(request.POST.get('score_d',0)),2)
    except:
        routine.score_d = 0
    try:
        routine.score_final = round(float(request.POST.get('score_final',0)),3)
    except:
        routine.score_final = 0

    if routine.status == Routine.ATHLETE_DONE:
        routine.status = Routine.REVIEW_DONE
        routine.save()
        app.firebase.routine_set_status(str(routine.session.id),routine.event.name,routine)
    else:
        routine.save()

    return HttpResponse(status=200)

def get_last_routine_status(request):
    return JsonResponse(Routine.objects.values().filter(session_id=request.POST.get('session'),d_judge=request.POST.get('this_judge'),event__name=request.POST.get('event')).order_by('-id').first(),safe=False)

def set_judges_participating(request):
    if request.POST.get('routine') != '-1':
        routine = Routine.objects.get(pk=request.POST.get('routine'))
        routine.e1_include = bool(distutils.util.strtobool(request.POST.get('e1')))
        routine.e2_include = bool(distutils.util.strtobool(request.POST.get('e2')))
        routine.e3_include = bool(distutils.util.strtobool(request.POST.get('e3')))
        routine.e4_include = bool(distutils.util.strtobool(request.POST.get('e4')))
    
        routine.save()
        app.firebase.routine_set_ejudge_include(str(routine.session.id) , routine.event.name,routine)
    return HttpResponse(status=200)

def set_judge_ready(request,session_id):
    judge = request.POST.get('judge')
    ready = True
    if request.POST.get('ready') == "false":
        ready = False
    app.firebase.routine_set_ejudge_ready(str(session_id), request.POST.get('event'),judge,ready)
    return HttpResponse(status=200)

@valid_login_type(match='e')
def ejudge_select(request):
    session = Session.objects.get(pk=request.session.get('session'))
    if session.use_ejudge_dots:
        context = {
            'title': 'E-Jury - ' + request.session.get("name"),
        }
        return render(request,'app/ejudge_select.html',context)
    else:
        return redirect('/evideo') 

@valid_login_type(match='e')
def ejudge(request):
    event = request.session.get('event')
    session = Session.objects.get(pk=request.session.get('session'))
    judges = Judge.objects.filter(session=session,event__name=event).first()
    disc = session.competition.disc.name
    ej = request.session.get('ej')

    if ej == 1:
        this_judge = judges.e1
    elif ej == 2:
        this_judge = judges.e2
    elif ej == 3:
        this_judge = judges.e3
    else:
        this_judge = judges.e4
    context = {
        'title': event + ' ' + session.competition.name,
        'judges':judges,
        'disc':disc,
        'event':event,
        'session':session,
        'ej':ej,
        'this_judge':this_judge,
    }
    return render(request,'app/ejudge.html',context)

@valid_login_type(match='e')
def evideo(request):
    event = request.session.get('event')
    session = Session.objects.get(pk=request.session.get('session'))
    judges = Judge.objects.filter(session=session,event__name=event).first()
    disc = session.competition.disc.name
    ej = request.session.get('ej')
    athletes = Athlete.objects.filter(team__session=session)
    if ej == 1:
        this_judge = judges.e1
    elif ej == 2:
        this_judge = judges.e2
    elif ej == 3:
        this_judge = judges.e3
    else:
        this_judge = judges.e4
    if event=="VT":
        help = 'ejudge_vault'
    else:
        help = 'ejudge'
    context = {
        'title': 'STS EJury - ' + event + ' ' + session.competition.name + ' - ' + this_judge,
        'judges':judges,
        'disc':disc,
        'event':event,
        'session':session,
        'ej':ej,
        'this_judge':this_judge,
        'athletes':athletes,
        'scoreboard':True,
        'help':help,
    }
    return render(request,'app/evideo.html',context)

@valid_login_type(match='d')
def d2_wag(request):
    event = request.session.get('event')
    session = Session.objects.get(pk=request.session.get('session'))
    judges = Judge.objects.filter(session=session,event__name=event).first()
    disc = session.competition.disc.name
    athletes = Athlete.objects.filter(team__session=session)
    context = {
        'title': 'STS D2 - ' + event + ' ' + session.competition.name + ' - ' + judges.d2,
        'judges':judges,
        'disc':disc,
        'event':event,
        'session':session,
        'this_judge':judges.d2,
        'athletes':athletes,
        'scoreboard':True,
        'help':help,
    }
    return render(request,'app/d2_wag.html',context)

def deduct(request):
    routine = request.POST.get('routine')
    judge = request.POST.get('judge')
    action = request.POST.get('judge','Add')
    relative_time = int(float(request.POST.get('spot','-1')))
    deduction = int(request.POST.get('deduction'))
    editor = request.POST.get('editor','E')
    artistry_type = request.POST.get('artistry_type','')

    mili = int(time() * 1000)
    routine = Routine.objects.get(pk=routine)
    if relative_time == -1:
        relative_time = mili - routine.start_time

    if routine.athlete_done_time != None and routine.event.name != 'VT' and routine.routine_length() < relative_time:
        relative_time = routine.routine_length()-50
    

    ded = EJuryDeduction(routine=routine,judge=judge,deduction=deduction,action=action,editor=editor,time_stamp=mili,time_stamp_relative=relative_time,artistry_type=artistry_type)
    ded.save()
    try:
        app.firebase.update_e_ping(routine.session.id,routine.event.name,judge,deduction)
    except:
        pass
    
    return HttpResponse(status=200) 

def deduction_change(request):
    id = int(request.POST.get('id'))
    editor = request.POST.get('editor')
    ded = int(request.POST.get('deduction'))
    #get the deduction
    deduction = EJuryDeduction.objects.get(pk=id)
    if deduction:
        #make sure the routine is not fully done
        #if deduction.routine.status == Routine.FINISHED:
             #return HttpResponse(status=403) 
        deduction.pk = None
        deduction.editor = editor
        if ded == 0:
            deduction.action = EJuryDeduction.DELETE
        else:
            deduction.action = EJuryDeduction.EDIT
        deduction.deduction = ded
        deduction.save()
    else:
        return HttpResponse(status=404) 

    return HttpResponse(status=200) 

def routine_get_info(request):
    return JsonResponse(Routine.objects.values().get(pk=request.POST.get('routine')),safe=False)

def build_dots(request):
    routine = request.POST.get('routine')
    judge = request.POST.get('judge','')
    width = int(request.POST.get('width',854))
    padding = int(request.POST.get('padding',17))
    dot_size = int(request.POST.get('dot_size',12))
    y_offset = int(request.POST.get('y_offset',22))
    playback_only = request.POST.get('playback_only','0')
    initial_offset = int(request.POST.get('initial_offset',25))
    if width == 0:
        width = 854
    delay=0
    #e1done = request.POST.get('e1done','true')
    #e2done = request.POST.get('e2done','true')
    #e3done = request.POST.get('e3done','true')
    #e4done = request.POST.get('e4done','true')
    prev_judge = ""
    prev_time = 0
    if judge != '':
        deductions = EJuryDeduction.objects.filter(routine_id=routine,judge=judge).order_by('judge','time_stamp_relative','-id')
        indicators = []
        all_judges = False
    else:
        deductions = EJuryDeduction.objects.filter(routine_id=routine).order_by('judge','time_stamp_relative','-id')
        indicators = DJuryIndicator.objects.filter(routine_id=routine,type=DJuryIndicator.CREDIT).order_by('time_stamp_relative','-id')
        all_judges = True

    routine = Routine.objects.get(pk=routine)
    routine_length = routine.athlete_done_time-routine.start_time
    deduction_list = []
    artistry_list = []
    judge_totals = {}
    vault_phases = [0,0,0,0,0]
    artistry_amounts = [0,0,0,0,0]
    total = 0

    for d in deductions:
        if prev_time != d.time_stamp_relative or prev_judge != d.judge:
            #set score
            if prev_judge != d.judge:
                if prev_judge != '':
                    judge_totals[prev_judge] = total/10
                total = 0
            total = total + d.deduction
            prev_time = d.time_stamp_relative
            prev_judge = d.judge
            opacity = 1
            #match judges
            if all_judges:
                j_offset = d.judge
                if d.judge == 1 and routine.e1_done == False:
                    opacity=0.3
                elif d.judge == 2 and routine.e2_done == False:
                    opacity=0.3
                elif d.judge == 3 and routine.e3_done == False:
                    opacity=0.3
                elif d.judge == 4 and routine.e4_done == False:
                    opacity=0.3
            else:
                j_offset = 1
            jumppos=-1
            if d.artistry_type != '':
                posx = (dot_size/8)
                posx = posx + ((dot_size + (dot_size/8))*artistry_amounts[j_offset])
                artistry_amounts[j_offset] += 1
            elif routine.event.name == "VT":
                posx = int(str(d.time_stamp_relative)[0]) - 1 #get first digit and subtract one
                posx = posx * ((width)/4)#multiply by 1/4 the total width
                if posx == 0:
                    posx = 25#so the judge name doesnt obscure it
                #posx = posx + dot_size/2
                posx_adjust = int(str(d.time_stamp_relative)[1]) * (dot_size + (dot_size/4)) #get second digit
                posx = posx + posx_adjust
                posx = posx + padding
                vault_phases[int(str(d.time_stamp_relative)[0])] += 1
                posx = 'left:' + str(posx)
            else:
                posx = ((d.time_stamp_relative + delay)/1000) /(routine_length/1000)
                jumppos=d.time_stamp_relative/1000
                posx = posx*100
                #posx = posx * (width-padding-padding)
                #posx = posx - ((dot_size/2)/width)
                #posx = posx + padding
                if posx >= 90:
                    posx = 100 - posx
                    if posx <= 0:
                        posx = 1
                    posx = 'right:' + str(posx)
                else:
                    posx = 'left:' + str(posx)
            posy = (j_offset-1)*y_offset + initial_offset
            posy = posy - (dot_size/2)
            if d.action == EJuryDeduction.EDIT:
                image = 'e-' + str(d.deduction) + 'e.svg'
            elif d.action == EJuryDeduction.DELETE:
                image = 'e-0e.svg'
            else:
                image = 'e-' + str(d.deduction) + '.svg'
            ded = {
                "posx":posx,
                "posy":posy,
                "image":image,
                "deduction":d.deduction,
                "id":d.id,
                "artistry_type":d.artistry_type,
                "opacity":opacity,
                "jumppos":jumppos,
                "judge":d.judge,
                }
            if d.artistry_type == '':
                deduction_list.append(ded)
            else:
                artistry_list.append(ded)

    judge_totals[prev_judge] = total/10

    #now djury junk
    indicator_list = []
    
    for i in indicators:
        posx = ((i.time_stamp_relative + delay)/1000) /(routine_length/1000)
        jumppos=i.time_stamp_relative/1000
        posx = posx*100
        if i.value == True:
            image = 'd-c.svg'
        else:
            image = 'd-n.svg'
        ind = {
            "posx":'left:' + str(posx),
            "posy":0,
            "image":image,
            "jumppos":jumppos,
            "opacity":1,
            "id":i.id,
            }
        indicator_list.append(ind)

    
    context = {
        'deductions': deduction_list,
        'routine':routine,
        'routine_length':routine.athlete_done_time-routine.start_time,
        'dot_size':dot_size,
        'judge_totals':judge_totals,
        'vault_phases':vault_phases,
        'artistry_deductions':artistry_list,
        'playback_only':playback_only,
        'indicators': indicator_list,
    }
    return render(request,'app/dots_area.html',context)

def accountability_report(request):
    routine = request.GET.get('routine')

    deductions = EJuryDeduction.objects.filter(routine_id=routine).order_by('judge','time_stamp_relative','id')
    routine = Routine.objects.get(pk=routine)

    prev_time = 0
    prev_judge = -1
    if routine.d1_done_time != None:
        routine_length = routine.d1_done_time-routine.start_time
    else:
        routine_length = 0
    deduction_list = []
    counter = 0
    judge_name = ''
    judge_deductions_numbers = [0,0,0,0,0]
    this_deduction_list = []
    for d in deductions:
        if prev_time != d.time_stamp_relative or prev_judge != d.judge:
            #new one
            if prev_judge != d.judge:
                counter = 0
                if d.judge == 1:
                    judge_name = routine.e1_name
                elif d.judge == 2:
                    judge_name = routine.e2_name
                elif d.judge == 3:
                    judge_name = routine.e3_name
                else:
                    judge_name = routine.e4_name
            counter += 1
            judge_deductions_numbers[d.judge] = counter
            if len(this_deduction_list) > 1:
                deduction_list.append(this_deduction_list)
            this_deduction_list = []
           
        this_deduction_list.append({'spot':d.time_stamp_relative,
                                    'judge':d.judge,
                                    'editor':d.editor,
                                    'name':judge_name,
                                    'deduction':d.deduction,
                                    'counter':counter})
        prev_time =  d.time_stamp_relative
        prev_judge = d.judge
    if len(this_deduction_list) > 1:
        deduction_list.append(this_deduction_list)
    context = {
        'deductions': deduction_list,
        'routine':routine,
        'judging_time':int(routine_length/1000),
        'counters':judge_deductions_numbers,
        'd1_name':routine.d1_name,
    }
    return render(request,'app/accountability_report.html',context)

def get_routines_by_SE(request):
    vals = ['athlete__name','athlete__team__name','athlete__level__name','athlete__age__name','id','score_e1','score_e2','score_e3','score_e4','score_e','score_d','score_final','score_neutral']
    level_filter = request.POST.get('level','-1')
    age_filter = request.POST.get('age','-1')
    if level_filter != '-1':
        if age_filter != '-1':
            routines = Routine.objects.values(*vals).filter(session_id=request.POST.get('Session'),event__name=request.POST.get('Ev'),status=Routine.FINISHED,athlete__level_id=level_filter,athlete__age_id=age_filter).order_by('id')
        else:
            routines = Routine.objects.values(*vals).filter(session_id=request.POST.get('Session'),event__name=request.POST.get('Ev'),status=Routine.FINISHED,athlete__level_id=level_filter).order_by('id')
    else:
        routines = Routine.objects.values(*vals).filter(session_id=request.POST.get('Session'),event__name=request.POST.get('Ev'),status=Routine.FINISHED).order_by('id')

    return JsonResponse(list(routines),safe=False)

def get_routines_aa(request):
    routines = Routine.objects.values('athlete__name','athlete__team__name','athlete__level__name','athlete__age__name').filter(session_id=request.POST.get('Session'),status=Routine.FINISHED).annotate(total_score=Sum('score_final')).order_by('-total_score')
        
    return JsonResponse(list(routines),safe=False)

def scoreboard_export(request,session_id):
    session = Session.objects.get(pk=session_id)
    teams = Team.objects.filter(session=session)
    events = Event.objects.filter(disc=session.competition.disc)
    return render(request, 'app/scoreboard_export.html', {'events':events,'teams':teams})

def scoreboard_export_get(request,session_id):
    session = Session.objects.get(pk=session_id)
    event_id = request.GET.get('event','-1')
    team_id = request.GET.get('team','-1')
    has_e = []
    values_list = ['athlete__level__name','athlete__age__name','athlete__team__name','athlete__name','score_d','score_neutral','score_e','score_e1','score_e2','score_e3','score_e4','score_final']
    if event_id != '-1':
        if team_id != '-1':
            routines = Routine.objects.filter(session=session,event_id=event_id,athlete__team_id=team_id,status=Routine.FINISHED).order_by('id')
        else:
            routines = Routine.objects.filter(session=session,event_id=event_id,status=Routine.FINISHED).order_by('id')
    else:
        if team_id != '-1':
            routines = Routine.objects.filter(session=session,athlete__team_id=team_id,status=Routine.FINISHED).order_by('event__order','id')
        else:
            routines = Routine.objects.filter(session=session,status=Routine.FINISHED).order_by('event__order','id')
    
    headers = ['Event','Level','Age Group', 'Team', 'Name', 'D-Score/Start Value','Neutral Deductions','E-Score/Deductions']  
    #find which es to include
    if len(routines.filter(score_e1__gt=0)) >= 1:
        has_e1 = True
        headers.append('E-1')
    else:
        has_e1 = False
    if len(routines.filter(score_e2__gt=0)) >= 1:
        has_e2 = True
        headers.append('E-2')
    else:
        has_e2 = False
    if len(routines.filter(score_e3__gt=0)) >= 1:
        has_e3 = True
        headers.append('E-3')
    else:
        has_e3 = False
    if len(routines.filter(score_e4__gt=0)) >= 1:
        has_e4 = True
        headers.append('E-4')
    else:
        has_e4 = False
         
    headers.append('Final Score')
    output = []
    response = HttpResponse (content_type='text/csv')
    writer = csv.writer(response)
    #Header
    writer.writerow(headers)
    for r in routines:
        out = [r.event.name,r.athlete.level.name,r.athlete.age.name,r.athlete.team.name,r.athlete.name,r.score_d,r.score_neutral,r.score_e]
        if has_e1:
            out.append(r.score_e1)
        if has_e2:
            out.append(r.score_e2)
        if has_e3:
            out.append(r.score_e3)
        if has_e4:
            out.append(r.score_e4)
        out.append(r.score_final)
        output.append(out)
    #CSV Data
    writer.writerows(output)
    return response


def scoreboard(request,event_name='-1'):
    session_in = request.GET.get('ses','')
    if session_in != '':
        if account.views.check_session_access_direct(request.user,session_in) == "No":
            return redirect('/select_session')
        request.session['session'] = session_in
    session = Session.objects.get(pk=request.session.get('session'))
    judges = Judge.objects.filter(session=session,event__name=event_name).first()
    #athletes = Athlete.objects.filter(session=session)
    events = Event.objects.filter(disc=session.competition.disc)
    if event_name == '-1':
        event_name = events.first().name

    levels = Athlete.objects.filter(team__session=session).values_list('level_id').distinct()
    levels = AthleteLevel.objects.filter(id__in=levels)
    show_filters = False
    if len(levels) == 1:
        #if only 1, check its ages
        ages = Athlete.objects.filter(team__session=session).values_list('age_id').distinct()
        ages = AthleteAge.objects.filter(id__in=ages)
        if len(ages) > 1:
            show_filters = True
    elif len(levels) > 1:
        show_filters = True

    if session.competition.disc.name == "WAG" and (session.level == Session.WDP or session.level == Session.NCAA): #d2_wag version
        total_only = True
    else:
        total_only = False
    context = {
        'title': session.full_name(),
        'judges':judges,
        'session':session,
        'events':events,
        'event_name':event_name,
        'exports':True,
        'total_only':total_only,
        'levels':levels,
        'show_filters':show_filters,
    }
    return render(request,'app/scoreboard.html',context)


def get_team_scores(request):
    if request.POST.get('Ev','') != 'AA':
        scores = calc_team_scores(request.POST.get('Session'),request.POST.get('Ev'))
        teams = Team.objects.filter(session_id=request.POST.get('Session'))
        team_scores = []
        for team in teams:
            this_score = next((s for s in scores if s['team'] == team.name),None)
            if this_score != None:
                team_scores.append({'team':team.name,'score':this_score['score']})
            else:
                team_scores.append({'team':team.name,'score':0.00})

    else:
        session = Session.objects.get(pk=request.POST.get('Session'))
        events = Event.objects.filter(disc=session.competition.disc)
        teams = Team.objects.filter(session_id=request.POST.get('Session'))
        team_scores = []
        for team in teams:
            team_scores.append({'team':team.name,'score':0.00})
   
        for event in events:
            scores = calc_team_scores(request.POST.get('Session'),event.name)
            for team in teams:
                this_score = next((s for s in scores if s['team'] == team.name),None)
                if this_score != None:
                    for t in team_scores:
                        if t['team'] == team.name:
                            t['score'] = t['score'] + this_score['score']
                            break
    
        for t in team_scores:
            t['score'] = "{:.2f}".format(t['score'])
        scores = team_scores

    #sort by score
    scores = sorted(scores,key = lambda i: i['score'],reverse=True)
    return JsonResponse(scores,safe=False)

def video_scoreboard(request):
    session = Session.objects.get(pk=request.GET.get('Session'))
    events = Event.objects.filter(disc=session.competition.disc)
    teams = Team.objects.filter(session_id=request.GET.get('Session'))
    team_scores = []
    for team in teams:
        team_scores.append({'team':team.abbreviation,'score':0.00,'dif':'--'})
   
    for event in events:
        scores = calc_team_scores(request.GET.get('Session'),event.name)
        for team in teams:
            this_score = next((s for s in scores if s['team'] == team.name),None)
            if this_score != None:
                for t in team_scores:
                    if t['team'] == team.abbreviation:
                        t['score'] = t['score'] + this_score['score']
                        break

    team_scores = sorted(team_scores,key = lambda i: i['score'],reverse=True)
    high = 0
    for t in team_scores:
        if t['score'] > high:
            high = t['score']
            t['dif'] = '--'
        else:
            t['dif'] = t['score'] - high
            if t['dif'] >= 0:
                t['dif'] = '--'
            else:
                t['dif'] = "{:.2f}".format(t['dif'])
        t['score'] = "{:.2f}".format(t['score'])

    #check which teams to show
    team_scores_filtered = []
    team_scores_filtered.append(team_scores[0]) #always show first
    if request.GET.get('Ath') != '-1' and request.GET.get('Ath') != '0':
        ath = Athlete.objects.get(pk=request.GET.get('Ath'))
        if team_scores[0]['team'] == ath.team.abbreviation:
            #highest is team up so just do them and second place
            team_scores_filtered.append(team_scores[1])
        else:
            for t in team_scores:
                if t['team'] == ath.team.abbreviation:
                    team_scores_filtered.append(t)
                    break
    else:
        team_scores_filtered.append(team_scores[1]) #just do first second as no team sent
    #team_scores = sorted(team_scores,key = lambda i: i['score'],reverse=True)
    context = {
        'scores': team_scores_filtered
        }
    return render(request,'app/video_scoreboard.html',context)

def calc_team_scores(session,event=''):
    if event != '':
        routines = Routine.objects.filter(session_id=session,event__name=event,status=Routine.FINISHED).order_by('athlete__team','athlete__level','-score_final')
    else:
        routines = Routine.objects.filter(session_id=session,status=Routine.FINISHED).order_by('athlete__team','athlete__level','-score_final')
    team = ""
    lvl = ""
    count = 0
    max = Session.objects.get(pk=session).top_counting_for_score
    scores = []
    for routine in routines:
        if team != routine.athlete.team.name:
            #setup new dict entry and set count to 0
            scores.append({'team': routine.athlete.team.name,'abbv':routine.athlete.team.abbreviation,'lvl':routine.athlete.level.name,'score':0})
            count = 0
            team = routine.athlete.team.name
            level = routine.athlete.level.name
        if count < max and routine.athlete.events_count_for_team.filter(name=routine.event.name).exists(): #fix routines to have actual event link not a freaking char field
            count += 1
            scores[-1]['score'] += routine.score_final
            scores[-1]['score'] = round(scores[-1]['score'],2)

    #sort by score
    scores = sorted(scores,key = lambda i: i['score'],reverse=True)
    return scores

def athlete_mark_done(request,athlete_id):
    event = request.session.get('event')
    session_id = request.session.get('session')
    athlete_mark_done_do(event,session_id,athlete_id)

    return HttpResponse(status=200)

def athlete_mark_done_do(event,session_id,athlete_id):
    sl = StartList.objects.filter(session_id=session_id,event__name=event,athlete_id=athlete_id).first()
    sl.completed=True
    sl.save()
    camera = Camera.objects.filter(teams=sl.athlete.team,events__name=event).first()
    check_update_camera_event(camera.session.id)

def athlete_get_next(request):
    event = request.session.get('event')
    session_id = request.session.get('session')
    sl = athlete_get_next_do(event,session_id)
    
    if sl != None:
        event_on = athlete_get_event_on(sl.athlete,session_id)
        return JsonResponse({'id':sl.athlete.id,
                            'label':str(sl.athlete),
                            'level':sl.athlete.level.name,
                            'team':str(sl.athlete.team),
                            'event_on':event_on})

    else:
        return JsonResponse({'id':'-1'})

def athlete_get_info(request,athlete_id):
    if athlete_id != 0:
        athlete = Athlete.objects.get(pk=athlete_id)

        return JsonResponse({'id':athlete.id,
                                'label':str(athlete),
                                'level':athlete.level.name,
                                'team':str(athlete.team)
                                })
    else:
        return JsonResponse({'id':0,
                                'label':'',
                                'level':'',
                                'team':''
                                })

def athlete_get_next_do(event,session_id):
    sl = StartList.objects.filter(session_id=session_id,event__name=event,active=True,completed=False,secondary_judging=False).order_by('order','athlete__rotation')
    #if skip_first:
    #   if len(sl) > 1:
    #        sl = sl[1]
    #    else:
    #        sl=None
    #else:
    sl=sl.first()
   
    return sl

def athlete_get_event_on(athlete,session_id):
    #t1 = perf_counter()
    next_event = 'done'
    rotation_order = RotationOrder.objects.filter(session_id=session_id,rotation=athlete.rotation).order_by('order')
    sls = StartList.objects.filter(athlete=athlete,session_id=session_id)
    for ord in rotation_order:
        sl = sls.get(event=ord.event)
        if sl.active and not sl.completed:
            next_event = sl.event.name
            break

    #print(perf_counter())
    return next_event

def athlete_start_list(request,event_name,team_id):
    session_id = request.session.get('session')
    start_list = StartList.objects.filter(session_id=session_id,event__name=event_name,completed=False,active=True).order_by('order','athlete__rotation')
    first_not_completed = -1
    if start_list.count() > 0:
        if team_id != 0:
            ath_rotation_team = Athlete.objects.filter(team_id=team_id,rotation=start_list[0].athlete.rotation).first()
            if ath_rotation_team == None:
                #not to this group yet
                start_list = None
            else:
                start_list=StartList.objects.filter(session_id=session_id,event__name=event_name,athlete__rotation=ath_rotation_team.rotation).order_by('order','athlete__rotation')
                fc = start_list.filter(completed=False,active=True,secondary_judging=False).first()
                first_not_completed = -1
                if fc != None:
                    if event_name == athlete_get_event_on(fc.athlete,session_id):
                        first_not_completed = fc.id
        else:
            rotation = start_list[0].athlete.rotation
            start_list=start_list.filter(athlete__rotation=rotation)
        
    context = {
        'start_list':start_list,
        'first_not_completed':first_not_completed,
    }
    return render(request,'app/athlete_start_list.html',context)

def athlete_start_list_admin(request,event_name):
    session_id = request.session.get('session')
    start_list = StartList.objects.filter(session_id=session_id,event__name=event_name).order_by('-completed','-secondary_judging','order','athlete__rotation')
    first_not_completed = start_list.filter(completed=False,active=True,secondary_judging=False).first()
    if first_not_completed != None:
        first_not_completed = first_not_completed.id
    else:
        first_not_completed = -1
    context = {
        'start_list':start_list,
        'first_not_completed':first_not_completed,
    }
    return render(request,'app/athlete_start_list_admin.html',context)

def athlete_start_list_swap(request,sl_id):
    sl = StartList.objects.get(pk=sl_id)
    start_list = StartList.objects.filter(session_id=sl.session.id,event=sl.event).exclude(id=sl_id).order_by('-completed','order','athlete__rotation')
    context = {
        'start_list':start_list,
        'sl_to_swap':sl,
    }
    return render(request,'app/athlete_start_list_swap.html',context)

def athlete_start_list_swap_do(request):
    sl_orig = StartList.objects.get(pk=request.POST.get('sl_orig'))
    sl_target = StartList.objects.get(pk=request.POST.get('sl_target'))
    #swap the numbers
    orig_order = sl_orig.order
    sl_orig.order = sl_target.order
    sl_target.order = orig_order
    
    orig_completed = sl_orig.completed
    sl_orig.completed = sl_target.completed
    sl_target.completed = orig_completed

    sl_orig.save()
    sl_target.save()
    
    #find routine on this event and swap
    rot_orig_swap_ids = list(Routine.objects.filter(athlete=sl_orig.athlete,event=sl_orig.event,session=sl_orig.session,status=Routine.FINISHED).values_list('id',flat=True))
    rot_target_swap_ids = list(Routine.objects.filter(athlete=sl_target.athlete,event=sl_target.event,session=sl_target.session,status=Routine.FINISHED).values_list('id',flat=True))
    Routine.objects.filter(id__in=rot_orig_swap_ids).update(athlete=sl_target.athlete)
    Routine.objects.filter(id__in=rot_target_swap_ids).update(athlete=sl_orig.athlete)

    athlete_start_list_change_check_manager(sl_orig.session.id,sl_orig.event.name)

    app.firebase.update_start_list(sl_orig.session.id,sl_orig.event.name)

    return HttpResponse(status=200)

def athlete_start_list_change_check_manager(session,event):

    #changing this to read from the local db as a firestore query is slooooooow
    #rot = Routine.objects.filter(session_id=session,event__name=event).order_by('-id').first()
    #if rot == None:
    #    get_next = True
    #    ath_id=-1
    #    status='N'
    #elif rot.status == Routine.NEW or rot.status == Routine.FINISHED or rot.status == Routine.DELETED:
    #    get_next = True
    #    ath_id = rot.athlete.id
    #    status = rot.status
    #if get_next:
    #    #previous routine all done so check first
    #    sl = athlete_get_next_do(event,session)
    #    if sl != None:
    #        camera = Camera.objects.filter(teams=sl.athlete.team,events__name=event).first()
    #        if sl.athlete.id !=ath_id or status == 'F':
    #            if status == 'F':
    #                app.firebase.routine_setup(sl.session,event,sl.athlete,camera.id,'D1')
    #            else:
    #                app.firebase.routine_update_athlete(session,event,sl.athlete,camera.id)
    rot = app.firebase.routine_get(session,event)

    if rot['status'] == 'N' or rot['status'] == 'F':
            #previous routine all done so check first
            sl = athlete_get_next_do(event,session)
            if sl != None:
                camera = Camera.objects.filter(teams=sl.athlete.team,events__name=event).first()
                if sl.athlete.id != rot['athlete_id'] or rot['status'] == 'F':
                    if rot['status'] == 'F':
                        app.firebase.routine_setup(sl.session,event,sl.athlete,camera.id,'D1')
                    else:
                        app.firebase.routine_update_athlete(session,event,sl.athlete,camera.id)
            check_update_camera_event(session)


def check_update_camera_event(session_id,camera = None):
    cameras = Camera.objects.filter(session_id=session_id)
    if camera != None:
        cameras = cameras.filter(id=camera.id)
    for cam in cameras:
        event_on = camera_get_event_on(cam)
        if cam.current_event != event_on:
            if event_on != None:
                cam.current_event = event_on
                cam.save()
                app.firebase.stream_set_event(cam.session.id,event_on.name,cam.id)
        

def camera_get_event_on(camera):
    #t1 = perf_counter()
    rotation = camera.teams.first().athlete_set.first().rotation
    next_event = None
    rotation_order = RotationOrder.objects.filter(session=camera.session,rotation=rotation).order_by('order')
    sls = StartList.objects.filter(athlete__rotation=rotation,session=camera.session,active=True,completed=False)#all un finished athletes on this rotation with no backup video
    for ord in rotation_order:
        sl = sls.filter(event=ord.event)
        for s in sl: #check to see if its just a backup video in which case dont move camera back
            if s.athlete.backupvideo_set.all().filter(event__name=ord.event.name).count() == 0:
                next_event = s.event
                break
        if next_event != None:
            break

    #print(perf_counter())
    return next_event

def athlete_start_list_spectate(request,event_name):
    session_id = request.session.get('session')
    this_rot = StartList.objects.filter(session_id=session_id,event__name=event_name,completed=False,active=True).first()
    if this_rot != None:
        this_rot = this_rot.athlete.rotation
    else:
        this_rot = 'Z'
    start_list = StartList.objects.filter(session_id=session_id,event__name=event_name,athlete__rotation=this_rot).order_by('-completed','-secondary_judging','order')
    total_this_rot = len(start_list.filter(active=True))
    first_not_completed = start_list.filter(completed=False,active=True,secondary_judging=False).first()
    #get first to make ordinal :( :( :(
    counter = 0
    ordinal = 0
    for sl in start_list.filter(active=True):
        counter = counter + 1
        if sl == first_not_completed:
            ordinal = make_ordinal(counter)
            break
    if first_not_completed != None:
        first_not_completed = first_not_completed.id
    else:
        first_not_completed = -1
    context = {
        'start_list':start_list,
        'first_not_completed':first_not_completed,
        'ordinal_total':str(ordinal) + ' of ' + str(total_this_rot),
        'ordinal':str(ordinal),
    }
    return render(request,'app/athlete_start_list_spectate.html',context)

def make_ordinal(n):
    '''
    Convert an integer into its ordinal representation::

        make_ordinal(0)   => '0th'
        make_ordinal(3)   => '3rd'
        make_ordinal(122) => '122nd'
        make_ordinal(213) => '213th'
    '''
    n = int(n)
    suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
    if 11 <= (n % 100) <= 13:
        suffix = 'th'
    return str(n) + suffix

def athlete_routine_remove(request):
    sl_orig = StartList.objects.get(pk=request.POST.get('sl_orig'))
   
    sl_orig.completed = False
    sl_orig.secondary_judging = False
    sl_orig.save()

    Routine.objects.filter(athlete=sl_orig.athlete,event=sl_orig.event,session=sl_orig.session,status=Routine.FINISHED).delete()

    athlete_start_list_change_check_manager(sl_orig.session.id,sl_orig.event.name)
    app.firebase.update_start_list(sl_orig.session.id,sl_orig.event.name)
    

    return HttpResponse(status=200)

def athlete_set_active(request,sl_id):
    sl = StartList.objects.get(pk=sl_id)
    if request.POST.get('active','1') == '1':
        sl.active = True
        #put them back in at end of current list for this rotation
        this_rotation = StartList.objects.filter(session=sl.session,event=sl.event,athlete__rotation=sl.athlete.rotation,active=True).order_by('-order')
        if len(this_rotation) > 0:
            #bump em all down one
            move_down = this_rotation.filter(order__gt=sl.order)
            if len(move_down) > 0:
                this_rotation.filter(order__gt=sl.order).update(order=F('order')-1)
                sl.order = this_rotation.first().order
        sl.save()
    else:
        if sl.secondary_judging and sl.completed == False:
            sl.secondary_judging = False
        sl.active = False
        sl.save()
    athlete_start_list_change_check_manager(sl.session.id,sl.event.name)
    app.firebase.update_start_list(sl.session.id,sl.event.name)

    return HttpResponse(status=200)

def athlete_start_list_update_order(request):
    session = Session.objects.get(pk=request.session.get('session'))
    sls = StartList.objects.filter(session=session,event__name=request.POST.get('ev'))
    sl_order = request.POST.get('sl_order').split(',')

    for index, val in enumerate(sl_order,start=1):
        sl = sls.get(pk=val)
        sl.order = index
        sl.save()

    athlete_start_list_change_check_manager(session.id,request.POST.get('ev'))
    app.firebase.update_start_list(session.id,request.POST.get('ev'))

    return HttpResponse(status=200)

@login_required(login_url='/account/login/admin/')
def reset_athlete_warn(request):
    return render(request,'app/reset_athlete_warn.html')

@login_required(login_url='/account/login/admin/')
def reset_athlete(request,session_id,event_name):
    #kill any secondary judging
    StartList.objects.filter(session_id=session_id,event__name=event_name,secondary_judging=True,completed=False).update(secondary_judging=False)
    sl = athlete_get_next_do(event_name,session_id)
    camera = Camera.objects.filter(teams=sl.athlete.team,events__name=event_name).first()
    app.firebase.routine_reset_previous(sl.session,event_name)
    app.firebase.routine_setup(sl.session,event_name,sl.athlete,camera.id,'D1')
    check_update_camera_event(camera.session.id,camera)

    return render(request,'app/reset_athlete_warn.html')

@valid_login_type(match='coach')
def coach(request,event_name='FX'):
    session_id = request.session.get('session')
    session = Session.objects.get(pk=session_id)
    team_id = request.session.get('team')
    team = Team.objects.get(pk=team_id)
    events = Event.objects.filter(disc=session.competition.disc)
    context = {
        'title': 'Coach - ' + team.abbreviation,
        'event_name':event_name,
        'events':events,
        'session':session,
        'team':team,
        'scoreboard':True,
        'help':'coach',
    }
    return render(request,'app/coach.html',context)

def athlete_mark_done_get_next(request,athlete_id):
    event = request.session.get('event')
    session_id = request.session.get('session')
    athlete_mark_done_do(event,session_id,athlete_id)
    sl = athlete_get_next_do(event,session_id)
   

    if sl != None:
        event_on = athlete_get_event_on(sl.athlete,session_id)
        return JsonResponse({'id':sl.athlete.id,
                             'label':str(sl.athlete),
                             'level':sl.athlete.level.name,
                             'team':str(sl.athlete.team),
                             'event_on':event_on})
    else:
        return JsonResponse({'id':'-1'})

def save_video(request):
    routine = Routine.objects.get(pk=request.POST.get('video-filename').replace(".webm",""))
    
    vidfile = settings.MEDIA_ROOT + '/routine_videos/' + str(routine.session.id) + '/' + routine.event.name + '/' + routine.athlete.name.replace(" ","") + "_" + request.POST.get('video-filename')
    os.makedirs(os.path.dirname(vidfile), exist_ok=True)
    output = open(vidfile, 'wb+')
    #output.write(request.FILES.get('video-blob').file.read())
    for chunk in request.FILES['video-blob'].chunks():
        output.write(chunk)
    output.close()
    routine.video_saved = True
    routine.video_file.name = 'routine_videos/' + str(routine.session.id) + '/' + routine.event.name + '/' + routine.athlete.name.replace(" ","") + "_" + request.POST.get('video-filename')
    routine.save()
    #os.system("ffmpeg -i {0} -c:v libx264 -profile:v main -vf format=yuv420p -c:a aac -movflags +faststart {1}".format(vidfile,vidfile.replace("webm","mp4")))
    #routine.video_converted = True
    #routine.save()
    #scheduler = BackgroundScheduler()
    #scheduler.add_job(convert_video,'interval', args=[settings.MEDIA_ROOT + '/routine_videos/' + request.POST.get('video-filename')], seconds=10)
    #scheduler.start()
    #scheduler.shutdown()
  
    return HttpResponse(status=200)

@login_required(login_url='/account/login/admin/')
def overview(request,session_id,event_name='-1'):
    request.session['session'] = session_id
    session = Session.objects.get(pk=request.session.get('session'))
    events = Event.objects.filter(disc=session.competition.disc)
    if event_name == '-1':
        event = events.first()
    else:
        event = events.filter(name=event_name).first()
    athletes = Athlete.objects.filter(team__session=session)
    judges = Judge.objects.filter(session=session,event=event).first()
    cameras = Camera.objects.filter(events=event,session=session)
    has_d2 = False
    if judges != None:
        if judges.d2_email != '':
            has_d2 = True

    setup_firebase_managers(session,event.name)
    
    context = {
        'title': 'Administrator Overview',
        'event_name':event.name,
        'events':events,
        'session':session,
        'scoreboard':True,
        'athletes':athletes,
        'judges':judges,
        'cameras':cameras,
        'has_d2':has_d2,
        'help':'admin_overview',
    }
    return render(request,'app/overview.html',context)

def setup_firebase_managers(session,event_name=''):
    events = Event.objects.filter(disc=session.competition.disc)
    if event_name != '':
        events = events.filter(name=event_name)
    for event in events:
        if not app.firebase.check_event_manager_setup(session.id,event.name):
            sl = athlete_get_next_do(event.name,session.id)
            if sl != None:
                athlete = sl.athlete
                #check for camera
                camera = Camera.objects.filter(teams=athlete.team,events__name=event.name).first()
                try:
                    app.firebase.routine_setup(session,event.name,athlete,camera.id,'D1')
                    check_update_camera_event(camera.session.id,camera)
                except:
                    pass
    

    return HttpResponse(status=200)

@login_required(login_url='/account/login/spectator/')
def select_session(request):

    context = {
        'title': 'Select Competition',
        'discs': Disc.objects.all(),
    }
    return render(request,'app/select_session.html',context)

def spectate(request,session_id,display_type,event_name='-1'):
    request.session['session'] = session_id
    session = Session.objects.get(pk=request.session.get('session'))
    #check for access
    if account.views.check_session_access_direct(request.user,session_id) == "No":
        return redirect('/select_session')
    events = Event.objects.filter(disc=session.competition.disc)
    if event_name == '-1':
        event = events.first()
    else:
        event = events.filter(name=event_name).first()
    athletes = Athlete.objects.filter(team__session=session)
    sponsors = Sponsor.objects.filter(session=session)
    
    event_name = event.name

    if display_type == 'dual':
        event_name2 = event.display_order + (events.count() / 2)
        if event_name2 > events.count():
            event_name2 = event_name2 - events.count()
        event_name2 = events.filter(display_order=event_name2).first().name
    else:
        event_name2 = ''
    #setup_firebase_managers(session,event.name)

    scoreboard_overlay = True
    #scoreboard_overlay = False
    #if session.competition.type == Competition.DUAL or session.competition.type == Competition.INTRASQUAD:
        #scoreboard_overlay = True

    context = {
        'title': 'Spectator',
        'event_name':event_name,
        'event_name2':event_name2,
        'events':events,
        'session':session,
        'scoreboard':True,
        'athletes':athletes,
        'sponsors':sponsors,
        'display_type':display_type,
        'scoreboard_overlay':scoreboard_overlay,
    }
    return render(request,'app/spectate.html',context)

def spectator_video(request):
    context = {
        'player_id':request.POST.get('player_id'),
    }
    return render(request,'app/spectator_video.html',context)

def comp(request,session_id):
    session = Session.objects.get(pk=session_id)
    #check for access
    if request.user.is_authenticated:
        access =  account.views.check_session_access_direct(request.user,session_id)
        if access == "Yes":
            return redirect('/spectate/' + str(session.id) + "/single/")
    else:
        access = "No"

    context = {
        'session':session,
        'access':access
    }
    return render(request,'app/comp.html',context)

def set_floor_timer(request):
    ath = Athlete.objects.filter(pk=request.POST.get('athlete')).first()
    if ath != None:
        if request.POST.get('started') == "true":
            started = True
        else:
            started = False
       
        app.firebase.set_floor_timer(ath.team.session.id,request.POST.get('event'),ath.team.id,started)

    return HttpResponse(status=200)

def set_fall(request):
    ath = Athlete.objects.filter(pk=request.POST.get('athlete')).first()
    routine = Routine.objects.filter(pk=request.POST.get('routine')).first()
    mili = int(time() * 1000)
    relative_time = mili - routine.start_time
    if ath != None:
        if request.POST.get('fall') == "true":
            fall = True
            if routine != None:
                djury_indicator = DJuryIndicator(routine=routine,time_stamp_relative=relative_time,type=DJuryIndicator.FALL,value=fall)
                djury_indicator.save()
        else:
            fall = False
       
        app.firebase.set_fall(ath.team.session.id,request.POST.get('event'),ath.team.id,fall)

    return HttpResponse(status=200)

def set_credit(request):
    ath = Athlete.objects.get(pk=request.POST.get('athlete'))
    routine = Routine.objects.get(pk=request.POST.get('routine'))
    mili = int(time() * 1000)
    relative_time = mili - routine.start_time
    if request.POST.get('credit') == "true":
        credit = "CREDIT AWARDED"
        val = True
    else:
        credit = "CREDIT NOT AWARDED"
        val = False
    djury_indicator = DJuryIndicator(routine=routine,time_stamp_relative=relative_time,type=DJuryIndicator.CREDIT,value=val)
    djury_indicator.save()
    app.firebase.set_credit(ath.team.session.id,request.POST.get('event'),ath.team.id,credit)

    return HttpResponse(status=200)

def backup_video_upload(request,session_id):
    if request.method == 'POST':
        form = VideoUploadForm(request.POST,request.FILES,session=session_id)
        if form.is_valid():
            #check for existing and delete
            og = BackupVideo.objects.filter(session=form.cleaned_data['session'],athlete=form.cleaned_data['athlete'],event=form.cleaned_data['event']).first()
            if og != None:
                og.video_file.delete()
                og.delete()
            bv = form.save()
            if bv.video_file.name.endswith(".mp4"):
                bv.converted = True
                bv.save()
            return render(request, 'app/backup_video_upload.html', {'form': form,'session_id':session_id,'bv':bv})
        else:
            return render(request, 'app/backup_video_upload.html', {'form': form,'session_id':session_id})
    else:
        #check for ownership
        if 'admin' in request.session['type']:
            s = Session.objects.filter(pk=session_id,competition__admin = request.user).first()
            if s == None and not request.user.is_staff:
                return HttpResponse(status=403)
            form = VideoUploadForm(session=session_id)
            return render(request, 'app/backup_video_upload.html', {'form': form,'session_id':session_id})
        else:
            if request.session.get('session') != session_id:
                return HttpResponse(status=403)
            form = VideoUploadForm(session=session_id,team=request.session.get('team'))
            return render(request, 'app/backup_video_upload.html', {'form': form,'session_id':session_id})

def backup_video_manage(request,session_id):
    session = Session.objects.filter(pk=session_id).first()
    if 'admin' in request.session['type']:
        s = Session.objects.filter(pk=session_id,competition__admin = request.user).first()
        team_restriction=0
        if s == None and not request.user.is_staff:
            return HttpResponse(status=403)
    elif 'coach' in request.session['type']:
        if request.session.get('session') != session_id:
            return HttpResponse(status=403)
        team_restriction=request.session['team']
    else:
        return HttpResponse(status=403)
    return render(request, 'app/backup_video_manage.html', {'session':session,'team_restriction':team_restriction})

def backup_video_list(request,session_id,team_restriction):
    if team_restriction != 0:
        backup_videos = BackupVideo.objects.filter(session_id=session_id,athlete__team_id = team_restriction).order_by('event__display_order','athlete__team','athlete__name')
    else:
        backup_videos = BackupVideo.objects.filter(session_id=session_id).order_by('event__display_order','athlete__team','athlete__name')
    return render(request, 'app/backup_video_list.html', {'backup_videos':backup_videos})

def backup_video_delete(request,backup_video_id):
    bv = BackupVideo.objects.filter(pk=backup_video_id).first()
    routine = Routine.objects.filter(session=bv.session,video_file=bv.video_file).first()
    if routine != None:
        return JsonResponse({'status':'reviewed'})
    else:
        try:
            bv.video_file.delete()
        except:
            pass
        bv.delete()
        return JsonResponse({'status':'ok'})

def backup_video_display(request,backup_video_id):
    bv = BackupVideo.objects.filter(pk=backup_video_id).first()
    return render(request, 'app/backup_video_display.html', {'bv':bv})

def check_backup_video_exists(request):
    bv = BackupVideo.objects.filter(session_id=request.GET.get('session'),athlete_id=request.GET.get('athlete'),event_id=request.GET.get('event')).first()
    if bv == None:
        resp = {'status':'ok'}
    elif bv.reviewed:
        resp = {'status':'reviewed'}
    else:
        resp = {'status':'exists'}

    return JsonResponse(resp)

def check_all_athletes_done(request,session_id):
    session = Session.objects.get(pk=session_id)
    sl = StartList.objects.filter(session=session,completed=False,active=True)
    if len(sl) == 0:
        return HttpResponse("Done")
    else:
        return HttpResponse(len(sl))

def session_mark_complete(request,session_id):
    session = Session.objects.get(pk=session_id)
    session.finished = True
    session.save()

    return HttpResponse(200)

def session_complete_warn(request):
    return render(request,'app/session_complete_warn.html')

def help(request,help_screen):
    return render(request, 'app/help/' + help_screen + '.html')

def wowza_broadcast(request):
    return render(request,'app/dev-view-publish.html')

def wowza_play(request):
    return render(request,'app/dev-view-play.html')

