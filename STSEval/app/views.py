"""
Definition of views.
"""

from django.shortcuts import render,redirect
from django.http import HttpRequest,JsonResponse,HttpResponse
from django.template import RequestContext
from datetime import datetime
from django.contrib.auth import authenticate, login
from app.models import Twitch,Routine,EJuryDeduction
from management.models import Competition,Judge,Athlete,Session,Camera
from app.twitch import TwitchAPI
import app.firebase
from time import time
from decimal import Decimal
from streaming.models import WowzaStream
from django.conf import settings
from binascii import a2b_base64
import distutils.util
import os

def valid_login_type(match=None):
    def decorator(func):
        def decorated(request, *args, **kwargs):
            if match in request.session.get('type'):
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
    routine = request.GET.get('routine','')
    if routine == '':
        event = request.session.get('event')
        session = Session.objects.get(pk=request.session.get('session'))
        judges = Judge.objects.filter(session=session,event__name=event)
        athletes = Athlete.objects.filter(team__session=session)
        disc = session.competition.disc.name
        layout = 'app/layout.html'
    else:
        routine = Routine.objects.get(pk=routine)
        session_id = routine.session.id
        disc = routine.disc
        event = routine.event
        judges = Judge.objects.filter(session_id=session_id,event__name=event)
        athletes = Athlete.objects.filter(session_id=session_id)
        session = routine.session
        layout = 'app/layout_empty.html'
        routine = routine.id
    context = {
        'title': 'D1 Overview - ' + event + ' ' + session.name,
        'judges':judges[0],
        'athletes':athletes,
        'disc':disc,
        'event':event,
        'session':session,
        'loadroutine':routine,
        'layout':layout
    }
    return render(request,'app/d1.html',context)

def routine_setup(request):
    athlete = Athlete.objects.get(pk=request.POST.get('athlete'))
    #check for camera
    camera = Camera.objects.filter(teams=athlete.team,events__name=request.session.get('event')).first()
    if camera == None:
        resp = {'routine':-1,
                 'error':'No Camera for ' + athlete.team.name + ' on ' + request.session.get('event') + '.  Contact your Meet Administrator'}
        return JsonResponse(resp)

    app.firebase.routine_setup(str(request.session.get('session')) + request.session.get('disc') + request.session.get('event'),athlete,camera.id)

    resp = {'routine':routine.id}
    return JsonResponse(resp)

def routine_start_judging(request):
    routine = Routine(session_id=request.session.get('session'),disc=request.session.get('disc'),event=request.session.get('event'),athlete_id=request.POST.get('athlete'))
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
    app.firebase.routine_set_status(str(request.session.get('session')) + request.session.get('disc') + request.session.get('event'),routine)

    return HttpResponse(status=200)

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
    app.firebase.routine_set_status(str(request.session.get('session')) + request.session.get('disc') + request.session.get('event'),routine)

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
    app.firebase.routine_set_ejudge_done(str(routine.session.id) + routine.disc + routine.event,judge,True)

    return HttpResponse(status=200)

def routine_delete(request):
    routine = Routine.objects.get(pk=request.POST.get('routine'))
    routine.status = Routine.DELETED

    routine.save()

    if os.path.exists('/' + settings.MEDIA_ROOT + '/routine_videos/' + str(routine.id) + '.webm'):
        os.remove('/' + settings.MEDIA_ROOT + '/routine_videos/' + str(routine.id) + '.webm')

    app.firebase.routine_set_status(str(routine.session.id) + routine.disc + routine.event,routine)

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
    app.firebase.routine_set_status(str(routine.session.id) + routine.disc + routine.event,routine)

    return HttpResponse(status=200)

def routine_set_score(request):
    routine = Routine.objects.get(pk=request.POST.get('routine'))
    routine.status = Routine.REVIEW_DONE
    try:
        routine.score_elements = int(request.POST.get('score_elements'))
    except:
        routine.score_elements = 0
    try:
        routine.score_difficulty = float(request.POST.get('score_difficulty'))
    except:
        routine.score_difficulty = 0
    try:
        routine.score_groups = float(request.POST.get('score_groups'))
    except:
        routine.score_groups = 0
    try:
        routine.score_bonus = float(request.POST.get('score_bonus'))
    except:
        routine.score_bonus = 0
    try:
        routine.score_neutral = float(request.POST.get('score_neutral'))
    except:
        routine.score_neutral = 0
    try:
        routine.score_e1 = float(request.POST.get('score_e1',0))
    except:
        routine.score_e1 = 0
    try:
        routine.score_e2 = float(request.POST.get('score_e2',0))
    except:
        routine.score_e2 = 0
    try:
        routine.score_e3 = float(request.POST.get('score_e3',0))
    except:
        routine.score_e3 = 0
    try:
        routine.score_e4 = float(request.POST.get('score_e4',0))
    except:
        routine.score_e4 = 0
    try:
        routine.score_e = float(request.POST.get('score_e',0))
    except:
        routine.score_e = 0
    try:
        routine.score_d = float(request.POST.get('score_d',0))
    except:
        routine.score_d = 0
    try:
        routine.score_final = float(request.POST.get('score_final',0))
    except:
        routine.score_final = 0

    routine.save()
    app.firebase.routine_set_status(str(routine.session.id) + routine.disc + routine.event,routine)

    return HttpResponse(status=200)

def set_judges_participating(request):
    routine = Routine.objects.get(pk=request.POST.get('routine'))
    routine.e1_include = bool(distutils.util.strtobool(request.POST.get('e1')))
    routine.e2_include = bool(distutils.util.strtobool(request.POST.get('e2')))
    routine.e3_include = bool(distutils.util.strtobool(request.POST.get('e3')))
    routine.e4_include = bool(distutils.util.strtobool(request.POST.get('e4')))
    
    routine.save()
    app.firebase.routine_set_ejudge_include(str(routine.session.id) + routine.disc + routine.event,routine)
    return HttpResponse(status=200)

@valid_login_type(match='e')
def ejudge_select(request):
    context = {
        'title': 'E-Jury - ' + request.session.get("name"),
    }
    return render(request,'app/ejudge_select.html',context)

@valid_login_type(match='e')
def ejudge(request):
    comp = request.GET.get('c')
    disc = request.GET.get('d')
    event = request.GET.get('e')
    ej = request.GET.get('ej')

    comp = Competition.objects.get(pk=comp)
    judges = Judge.objects.filter(session_id=comp,disc=disc,event=event).first()
    if ej == '1':
        this_judge = judges.e1
    elif ej == '2':
        this_judge = judges.e2
    elif ej == '3':
        this_judge = judges.e3
    else:
        this_judge = judges.e4
    context = {
        'title': 'STS EJury - ' + event + ' ' + comp.name,
        'judges':judges,
        'disc':disc,
        'event':event,
        'comp':comp,
        'ej':ej,
        'this_judge':this_judge,
    }
    return render(request,'app/ejudge.html',context)

@valid_login_type(match='e')
def evideo(request):
    comp = request.GET.get('c')
    disc = request.GET.get('d')
    event = request.GET.get('e')
    ej = request.GET.get('ej')
    comp = Competition.objects.get(pk=comp)
    judges = Judge.objects.filter(session_id=comp,disc=disc,event=event).first()
    athletes = Athlete.objects.filter(session_id=request.GET.get('c'),disc=request.GET.get('d'))
    if ej == '1':
        this_judge = judges.e1
    elif ej == '2':
        this_judge = judges.e2
    elif ej == '3':
        this_judge = judges.e3
    else:
        this_judge = judges.e4
    context = {
        'title': 'STS EJury - ' + event + ' ' + comp.name + ' - ' + this_judge,
        'judges':judges,
        'disc':disc,
        'event':event,
        'comp':comp,
        'ej':ej,
        'this_judge':this_judge,
        'athletes':athletes
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

    if routine.athlete_done_time != None and routine.event != 'V':
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
        if deduction.routine.status == Routine.FINISHED:
             return HttpResponse(status=403) 
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

def get_routines_by_DCE(request):
    routines = Routine.objects.values('athlete__name','athlete__team','athlete__level','id','score_e1','score_e2','score_e3','score_e4','score_e','score_d','score_final').filter(session_id=request.POST.get('session'),disc=request.POST.get('Disc'),event=request.POST.get('Ev'),status=Routine.FINISHED).order_by('id')
    return JsonResponse(list(routines),safe=False)

def scoreboard(request):
    comp = request.GET.get('c')
    disc = request.GET.get('d')
    event = request.GET.get('e')
    comp = Competition.objects.get(pk=comp)
    judges = Judge.objects.filter(session_id=comp,disc=disc,event=event)
    athletes = Athlete.objects.filter(session_id=request.GET.get('c'),disc=request.GET.get('d'))
    events = []
    if disc == "MAG":
        events.append('fx')
        events.append('ph')
        events.append('r')
        events.append('v')
        events.append('pb')
        events.append('hb')
    elif disc == "WAG":
        events.append('v')
        events.append('ub')
        events.append('bb')
        events.append('fx')
    context = {
        'title': 'Scoreboard - ' + event + ' ' + comp.name,
        'judges':judges[0],
        'athletes':athletes,
        'disc':disc,
        'event':event,
        'comp':comp,
        'events':events,
    }
    return render(request,'app/scoreboard.html',context)

def save_video(request):
    output = open('/' + settings.MEDIA_ROOT + '/routine_videos/' + request.POST.get('video-filename'), 'wb+')
    #output.write(request.FILES.get('video-blob').file.read())
    for chunk in request.FILES['video-blob'].chunks():
        output.write(chunk)
    output.close()
  
    return HttpResponse(status=200)

def wowza_broadcast(request):
    return render(request,'app/dev-view-publish.html')

def wowza_play(request):
    return render(request,'app/dev-view-play.html')

