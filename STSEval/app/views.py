"""
Definition of views.
"""

from django.shortcuts import render,redirect
from django.http import HttpRequest,JsonResponse,HttpResponse
from django.template import RequestContext
from datetime import datetime
from django.contrib.auth import authenticate, login
from app.models import Twitch,Routine,EJuryDeduction,BackupVideo
from management.models import Competition,Judge,Athlete,Session,Camera,StartList,Team,Event,Disc,Sponsor
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
        multi_d = True
    else:
        multi_d = False
    
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

    }
    return render(request,'app/d1.html',context)

def view_routine(request,routine_id,popup):
    routine = Routine.objects.get(pk=routine_id)
    event = routine.event
    session_id = routine.session.id
    judges = Judge.objects.filter(session_id=session_id,event__name=event)
    athletes = Athlete.objects.filter(team__session_id=session_id)
    session = routine.session
    if popup == 1:
        layout = 'app/layout_empty.html'
    else:
        layout = 'app/layout.html'
    editable = False
    if 'd1' in request.session.get('type') or 'd2' in request.session.get('type'):#d1 can edit if its their event
        if request.session.get('event','').lower() == event.lower():
            editable = True
    elif 'admin' in request.session.get('type'):#admin can always edit
        editable = True

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
        'multi_d':False,
    }
    return render(request,'app/d1.html',context)

def d1_edit_score(request,routine_id):
    routine = Routine.objects.get(pk=routine_id)
    event = routine.event
    loadroutine = ''
    if 'd1' in request.session.get('type'):#d1 can edit if its their event
        if request.session.get('event','').lower() == event.lower():
            loadroutine = routine
    elif 'admin' in request.session.get('type'):#admin can always edit
        loadroutine = routine

    context = {
        'loadroutine':routine,
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

        return HttpResponse(status=200)
    else:
        return HttpResponse(status=404)

def routine_swap_d(request):
    #update this routine and check if it should swap
    routine = Routine.objects.get(pk=request.POST.get('routine'))
    sl = StartList.objects.filter(session=routine.session,event__name=routine.event,athlete=routine.athlete).first()
    sl.secondary_judging=True
    sl.save()

    sl = athlete_get_next_do(routine.event,routine.session.id)
    if sl != None:
        next_rotation = sl.athlete.rotation
    else:
        next_rotation = ''
    judges = Judge.objects.filter(session=routine.session,event__name=routine.event).first()
    if judges.d2_email != '' and next_rotation == routine.athlete.rotation:
        #d2 was filled out and this wasnt last gymnast in rotation, swap d judges
        if routine.d_judge == 'D1':
            next_judge = 'D2'
        else:
            next_judge = 'D1'
        camera = Camera.objects.filter(teams=sl.athlete.team,events__name=routine.event).first()
        app.firebase.routine_setup(routine.session,routine.event,sl.athlete,camera.id,next_judge)
        app.firebase.routine_set_status(routine.session.id,routine.event,routine)

    return HttpResponse(status=200)

def routine_start_judging(request):
    routine = Routine(session_id=request.session.get('session'),disc=request.session.get('disc'),event=request.session.get('event'),athlete_id=request.POST.get('athlete'),d_judge=request.POST.get('djudge','D1'))
    judges = Judge.objects.filter(session_id=request.session.get('session'),event__name=request.session.get('event')).first()
    routine.e1_name = judges.e1
    routine.e2_name = judges.e2
    routine.e3_name = judges.e3
    routine.e4_name = judges.e4
    routine.d1_name = judges.d1
    #routine = Routine.objects.filter(session_id=request.session.get('session'),disc=request.session.get('disc'),event=request.session.get('event')).order_by('-id').first()
    routine.status = Routine.STARTED
    routine.athlete_id=request.POST.get('athlete')

    mili = int(time() * 1000)
    routine.start_time = mili

    routine.save()
    app.firebase.routine_set_status(str(request.session.get('session')),request.session.get('event'),routine)

    resp = {'routine':routine.id}
    return JsonResponse(resp)

def routine_athlete_done(request):
    routine = Routine.objects.filter(session_id=request.session.get('session'),disc=request.session.get('disc'),event=request.session.get('event')).order_by('-id').first()
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
    app.firebase.routine_set_ejudge_done(str(routine.session.id),routine.event,judge,True)

    return HttpResponse(status=200)

def routine_delete(request):
    routine = Routine.objects.get(pk=request.POST.get('routine'))
    routine.status = Routine.DELETED

    routine.save()

    if os.path.exists('/' + settings.MEDIA_ROOT + '/routine_videos/' + str(routine.id) + '.webm'):
        os.remove('/' + settings.MEDIA_ROOT + '/routine_videos/' + str(routine.id) + '.webm')

    app.firebase.routine_set_status(str(routine.session.id),routine.event,routine)

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
    
    routine.save()
    app.firebase.routine_set_status(str(routine.session.id) ,routine.event,routine)

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
        app.firebase.routine_set_status(str(routine.session.id),routine.event,routine)
    else:
        routine.save()

    return HttpResponse(status=200)

def get_last_routine_status(request):
    return JsonResponse(Routine.objects.values().filter(session_id=request.POST.get('session'),d_judge=request.POST.get('this_judge'),event=request.POST.get('event')).order_by('-id').first(),safe=False)

def set_judges_participating(request):
    if request.POST.get('routine') != '-1':
        routine = Routine.objects.get(pk=request.POST.get('routine'))
        routine.e1_include = bool(distutils.util.strtobool(request.POST.get('e1')))
        routine.e2_include = bool(distutils.util.strtobool(request.POST.get('e2')))
        routine.e3_include = bool(distutils.util.strtobool(request.POST.get('e3')))
        routine.e4_include = bool(distutils.util.strtobool(request.POST.get('e4')))
    
        routine.save()
        app.firebase.routine_set_ejudge_include(str(routine.session.id) , routine.event,routine)
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
    context = {
        'title': 'E-Jury - ' + request.session.get("name"),
    }
    return render(request,'app/ejudge_select.html',context)

@valid_login_type(match='e')
def ejudge(request):
    event = request.session.get('event')
    session = Session.objects.get(pk=request.session.get('session'))
    judges = Judge.objects.filter(session=session,event__name=event).first()
    disc = session.competition.disc.name
    ej = request.session.get('ej')

    if ej == '1':
        this_judge = judges.e1
    elif ej == '2':
        this_judge = judges.e2
    elif ej == '3':
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
    if ej == '1':
        this_judge = judges.e1
    elif ej == '2':
        this_judge = judges.e2
    elif ej == '3':
        this_judge = judges.e3
    else:
        this_judge = judges.e4
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
    }
    return render(request,'app/evideo.html',context)

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

    if routine.athlete_done_time != None and routine.event != 'V' and routine.routine_length() < relative_time:
        relative_time = routine.routine_length()-50
    

    ded = EJuryDeduction(routine=routine,judge=judge,deduction=deduction,action=action,editor=editor,time_stamp=mili,time_stamp_relative=relative_time,artistry_type=artistry_type)
    ded.save()
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
    initial_offset = int(request.POST.get('initial_offset',15))
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
        all_judges = False
    else:
        deductions = EJuryDeduction.objects.filter(routine_id=routine).order_by('judge','time_stamp_relative','-id')
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
            elif routine.event == "V":
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
                }
            if d.artistry_type == '':
                deduction_list.append(ded)
            else:
                artistry_list.append(ded)

    judge_totals[prev_judge] = total/10
    context = {
        'deductions': deduction_list,
        'routine':routine,
        'routine_length':routine.athlete_done_time-routine.start_time,
        'dot_size':dot_size,
        'judge_totals':judge_totals,
        'vault_phases':vault_phases,
        'artistry_deductions':artistry_list,
        'playback_only':playback_only
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
    routines = Routine.objects.values('athlete__name','athlete__team__name','athlete__level__name','id','score_e1','score_e2','score_e3','score_e4','score_e','score_d','score_final','score_neutral').filter(session_id=request.POST.get('Session'),event=request.POST.get('Ev'),status=Routine.FINISHED).order_by('id')

    return JsonResponse(list(routines),safe=False)

def get_routines_aa(request):
    routines = Routine.objects.values('athlete__name','athlete__team__name','athlete__level__name').filter(session_id=request.POST.get('Session'),status=Routine.FINISHED).annotate(total_score=Sum('score_final')).order_by('-total_score')
        
    return JsonResponse(list(routines),safe=False)

@valid_login_type(match='session')
def scoreboard(request,event_name='-1'):
    session = Session.objects.get(pk=request.session.get('session'))
    judges = Judge.objects.filter(session=session,event__name=event_name).first()
    #athletes = Athlete.objects.filter(session=session)
    events = Event.objects.filter(disc=session.competition.disc)
    if event_name == '-1':
        event_name = events.first().name
    context = {
        'title': session.full_name(),
        'judges':judges,
        'session':session,
        'events':events,
        'event_name':event_name,
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
        team_scores.append({'team':team.abbreviation,'score':0.00})
   
    for event in events:
        scores = calc_team_scores(request.GET.get('Session'),event.name)
        for team in teams:
            this_score = next((s for s in scores if s['team'] == team.name),None)
            if this_score != None:
                for t in team_scores:
                    if t['team'] == team.abbreviation:
                        t['score'] = t['score'] + this_score['score']
                        break
    
    for t in team_scores:
        t['score'] = "{:.2f}".format(t['score'])
    #team_scores = sorted(team_scores,key = lambda i: i['score'],reverse=True)
    context = {
        'scores': team_scores
        }
    return render(request,'app/video_scoreboard.html',context)

def calc_team_scores(session,event=''):
    if event != '':
        routines = Routine.objects.filter(session_id=session,event=event,status=Routine.FINISHED).order_by('athlete__team','athlete__level','-score_final')
    else:
        routines = Routine.objects.filter(session_id=session,status=Routine.FINISHED).order_by('athlete__team','athlete__level','-score_final')
    team = ""
    lvl = ""
    count = 0
    max = 5
    scores = []
    for routine in routines:
        if team != routine.athlete.team.name or level != routine.athlete.level.name:
            #setup new dict entry and set count to 0
            scores.append({'team': routine.athlete.team.name,'abbv':routine.athlete.team.abbreviation,'lvl':routine.athlete.level.name,'score':0})
            count = 0
            team = routine.athlete.team.name
            level = routine.athlete.level.name
        if count < max and routine.athlete.events_count_for_team.filter(name=routine.event).exists(): #fix routines to have actual event link not a freaking char field
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
    athlete = Athlete.objects.get(pk=athlete_id)

    return JsonResponse({'id':athlete.id,
                            'label':str(athlete),
                            'level':athlete.level.name,
                            'team':str(athlete.team)
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
    rotation_basis = ord('A')
    rotation_adjust = ord(athlete.rotation) - rotation_basis #get the offset for order by
    next_event = 'done'
    sl = StartList.objects.filter(athlete=athlete,session_id=session_id).order_by('event__display_order')
    for i in range(sl.count()):
        j = i + rotation_adjust
        if j >= sl.count():
            j = j - sl.count()
        if sl[j].active and not sl[j].completed:
            next_event = sl[j].event.name
            break
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
    rot_orig_swap_ids = list(Routine.objects.filter(athlete=sl_orig.athlete,event=sl_orig.event.name,session=sl_orig.session,status=Routine.FINISHED).values_list('id',flat=True))
    rot_target_swap_ids = list(Routine.objects.filter(athlete=sl_target.athlete,event=sl_target.event.name,session=sl_target.session,status=Routine.FINISHED).values_list('id',flat=True))
    Routine.objects.filter(id__in=rot_orig_swap_ids).update(athlete=sl_target.athlete)
    Routine.objects.filter(id__in=rot_target_swap_ids).update(athlete=sl_orig.athlete)

    athlete_start_list_change_check_manager(sl_orig.session.id,sl_orig.event.name)

    app.firebase.update_start_list(sl_orig.session.id,sl_orig.event.name)

    return HttpResponse(status=200)

def athlete_start_list_change_check_manager(session,event):
    rot = app.firebase.routine_get(session,event)
    if rot['status'] == 'N' or rot['status'] == 'F':
            #previous routine all done so check first
            sl = athlete_get_next_do(event,session)
            camera = Camera.objects.filter(teams=sl.athlete.team,events__name=event).first()
            if sl.athlete.id != rot['athlete_id'] or rot['status'] == 'F':
                if rot['status'] == 'F':
                    app.firebase.routine_setup(sl.session,event,sl.athlete,camera.id,'D1')
                else:
                    app.firebase.routine_update_athlete(session,event,sl.athlete,camera.id)



def athlete_routine_remove(request):
    sl_orig = StartList.objects.get(pk=request.POST.get('sl_orig'))
   
    sl_orig.completed = False
    sl_orig.secondary_judging = False
    sl_orig.save()

    Routine.objects.filter(athlete=sl_orig.athlete,event=sl_orig.event.name,session=sl_orig.session,status=Routine.FINISHED).delete()

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
    vidfile = settings.MEDIA_ROOT + '/routine_videos/' + request.POST.get('video-filename')
    output = open(vidfile, 'wb+')
    #output.write(request.FILES.get('video-blob').file.read())
    for chunk in request.FILES['video-blob'].chunks():
        output.write(chunk)
    output.close()
    routine = Routine.objects.get(pk=request.POST.get('video-filename').replace(".webm",""))
    routine.video_saved = True
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
    judges = Judge.objects.filter(session=session,event=event)
    cameras = Camera.objects.filter(events=event,session=session)
    if judges.first().d2_email != '':
        has_d2 = True
    else:
        has_d2 = False
    setup_firebase_managers(session,event.name)
    
    context = {
        'title': 'Administrator',
        'event_name':event.name,
        'events':events,
        'session':session,
        'scoreboard':True,
        'athletes':athletes,
        'judges':judges.first(),
        'cameras':cameras,
        'has_d2':has_d2,
    }
    return render(request,'app/overview.html',context)

def setup_firebase_managers(session,event_name=''):
    events = Event.objects.filter(disc=session.competition.disc)
    if event_name != '':
        events = events.filter(name=event_name)
    for event in events:
        if not app.firebase.check_event_manager_setup(session.id,event.name):
            sl = athlete_get_next_do(event.name,session.id)
            athlete = sl.athlete
            #check for camera
            camera = Camera.objects.filter(teams=athlete.team,events__name=event.name).first()
            try:
                app.firebase.routine_setup(session,event.name,athlete,camera.id,'D1')
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

    scoreboard_overlay = False
    if session.competition.type == Competition.DUAL or session.competition.type == Competition.INTRASQUAD:
        scoreboard_overlay = True

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

def set_fall(request):
    ath = Athlete.objects.filter(pk=request.POST.get('athlete')).first()
    if ath != None:
        if request.POST.get('fall') == "true":
            fall = True
        else:
            fall = False
        app.firebase.set_fall(ath.team.session.id,request.POST.get('event'),ath.team.id,fall)

    return HttpResponse(status=200)

def set_credit(request):
    ath = Athlete.objects.get(pk=request.POST.get('athlete'))
    if request.POST.get('credit') == "true":
        credit = "CREDIT AWARDED"
    else:
        credit = "CREDIT NOT AWARDED"
    app.firebase.set_credit(ath.team.session.id,request.POST.get('event'),ath.team.id,credit)


@login_required(login_url='/account/login/admin/')
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
        s = Session.objects.filter(pk=session_id,competition__admin = request.user).first()
        if s == None and request.user.is_staff:
            return HttpResponse(status=403)
        form = VideoUploadForm(session=session_id)
        return render(request, 'app/backup_video_upload.html', {'form': form,'session_id':session_id})

@login_required(login_url='/account/login/admin/')
def backup_video_manage(request,session_id):
    session = Session.objects.filter(pk=session_id).first()
    return render(request, 'app/backup_video_manage.html', {'session':session})

def backup_video_list(request,session_id):
    backup_videos = BackupVideo.objects.filter(session_id=session_id).order_by('event__display_order','athlete__team','athlete__name')
    return render(request, 'app/backup_video_list.html', {'backup_videos':backup_videos})

def backup_video_delete(request,backup_video_id):
    bv = BackupVideo.objects.filter(pk=backup_video_id).first()
    if bv.reviewed:
        return JsonResponse({'status':'reviewed'})
    else:
        bv.video_file.delete()
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

def wowza_broadcast(request):
    return render(request,'app/dev-view-publish.html')

def wowza_play(request):
    return render(request,'app/dev-view-play.html')

