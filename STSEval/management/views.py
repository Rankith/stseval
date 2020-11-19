from django.shortcuts import render,redirect
from django.http import HttpRequest,JsonResponse,HttpResponse
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import datetime
from .forms import CompetitionForm,SessionForm,JudgeForm,TeamForm,AthleteForm,CameraForm,SponsorForm
from .models import Competition,Session,Athlete,Judge,Team,Disc,Event,Camera,Sponsor,StartList
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required,user_passes_test
from django.db.models import Count
from django.core.mail import get_connection, EmailMultiAlternatives
import app.views

# Create your views here.
@login_required(login_url='/account/login/admin/')
def setup_competition(request):

    context = {
        'title': 'Competition Setup (1/6)',
        'discs': Disc.objects.all(),
    }
    return render(request,'management/setup_competition.html',context)

def competition_list(request):
    comps = Competition.objects.filter(disc=request.GET.get('disc'),admin=request.user)

    context = {
        'comps':comps,
    }
    return render(request, 'management/competition_list.html', context)

def competition_list_all(request):
    if request.GET.get('current','0') == '0':
        comps = Competition.objects.filter(disc=request.GET.get('disc'))
    else:
        comps = Competition.objects.filter(disc=request.GET.get('disc'),date__gte=datetime.datetime.now() - datetime.timedelta(days=2),finished=False)

    context = {
        'comps':comps,
    }
    return render(request, 'management/competition_list.html', context)

@login_required(login_url='/account/login/admin/')
def competition_form(request):
    if request.method == 'POST':
        id = request.POST.get('id','-1')
        if id != '-1':
            form = CompetitionForm(request.POST,instance=Competition.objects.get(pk=id),user=request.user)
        else:
            form = CompetitionForm(request.POST,user=request.user)
        if form.is_valid():
            form.save()
            return HttpResponse(status=200)
        else:
            return render(request, 'management/competition_form.html', {'form': form,'id':id})
    else:
        id = request.GET.get('id',-1)
        if id != -1:
            form = CompetitionForm(instance=Competition.objects.get(pk=id),user=request.user)
        else:
            form = CompetitionForm(user=request.user)
        return render(request, 'management/competition_form.html', {'form': form,'id':id})

@login_required(login_url='/account/login/admin/')
def competition_delete(request):
    Competition.objects.filter(id=request.GET.get('id')).delete()
    return HttpResponse(status=200)

def session_list(request):
    sessions = Session.objects.filter(competition_id=request.GET.get('comp'))

    context = {
        'sessions':sessions,
    }
    return render(request, 'management/session_list.html', context)

@login_required(login_url='/account/login/admin/')
def session_form(request):
    if request.method == 'POST':
        id = request.POST.get('id','-1')
        if id != '-1':
            form = SessionForm(request.POST,instance=Session.objects.get(pk=id))
        else:
            form = SessionForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponse(status=200)
        else:
            return render(request, 'management/session_form.html', {'form': form,'id':id})
    else:
        id = request.GET.get('id',-1)
        if id != -1:
            form = SessionForm(instance=Session.objects.get(pk=id))
        else:
            form = SessionForm()
        return render(request, 'management/session_form.html', {'form': form,'id':id})

@login_required(login_url='/account/login/admin/')
def session_delete(request):
    Session.objects.filter(id=request.GET.get('id')).delete()
    return HttpResponse(status=200)

@login_required(login_url='/account/login/admin/')
def setup_judges(request,id):
    session = Session.objects.get(pk=id)
    events = Event.objects.filter(disc=session.competition.disc)
   
    context = {
        'title': 'Competition Setup (2/6)',
        'session_name': session.full_name,
        'events':events,
        'id':session.id,
    }
    return render(request,'management/setup_judges.html',context)

@login_required(login_url='/account/login/admin/')
def judge_form(request):
    if request.method == 'POST':
        id = request.POST.get('id','-1')
        if id != '-1':
            form = JudgeForm(request.POST,instance=Judge.objects.get(pk=id))
        else:
            form = JudgeForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponse(status=200)
        else:
            return render(request, 'management/judge_form.html', {'form': form,'id':id})
    else:
        judge = Judge.objects.filter(session_id=request.GET.get('session'),event=request.GET.get('event'))
        if len(judge) > 0:
            id=judge[0].id
            form = JudgeForm(instance=judge[0])
        else:
            id=-1
            form = JudgeForm()
        return render(request, 'management/judge_form.html', {'form': form,'id':id})

def judges_check_missing(request,session_id):
    missed = judges_check_missing_call(session_id)

    return JsonResponse({'missed':list(missed)})

def judges_check_missing_call(session_id):
    #see if d1 judge is assigned
    session = Session.objects.get(pk=session_id)
    events = Event.objects.filter(disc=session.competition.disc).order_by('display_order')
    judges = Judge.objects.filter(session=session)
    missed = []

    for event in events:
        judge = judges.filter(event=event).first()
        if judge != None:
            if judge.d1_email == '':
                missed.append(event.name)
        else:
            missed.append(event.name)

    return missed

@login_required(login_url='/account/login/admin/')
def setup_athletes(request,id):
    session = Session.objects.get(pk=id)
    context = {
        'title': 'Competition Setup (3/6)',
        'session_name': session.full_name,
        'id':session.id,
    }
    return render(request,'management/setup_athletes.html',context)

@login_required(login_url='/account/login/admin/')
def team_form(request):
    if request.method == 'POST':
        id = request.POST.get('id','-1')
        if id != '-1':
            form = TeamForm(request.POST,instance=Team.objects.get(pk=id))
        else:
            form = TeamForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponse(status=200)
        else:
            return render(request, 'management/team_form.html', {'form': form,'id':id})
    else:
        id = request.GET.get('id',-1)
        if id != -1:
            form = TeamForm(instance=Team.objects.get(pk=id))
        else:
            form = TeamForm()
        return render(request, 'management/team_form.html', {'form': form,'id':id})

@login_required(login_url='/account/login/admin/')
def team_list(request,session_id):
    teams = Team.objects.filter(session_id=session_id)
    context = {
        'teams':teams,
    }
    return render(request, 'management/team_list.html', context)

@login_required(login_url='/account/login/admin/')
def team_delete(request,id):
    Team.objects.filter(id=id).delete()
    return HttpResponse(status=200)

@login_required(login_url='/account/login/admin/')
def athlete_form(request):
    if request.method == 'POST':
        id = request.POST.get('id','-1')
        if id != '-1':
            athlete = Athlete.objects.get(pk=id)
            form = AthleteForm(request.POST,instance=athlete,session=athlete.team.session.id)
        else:
            team = Team.objects.get(pk=request.POST.get('team'))
            form = AthleteForm(request.POST,session=team.session.id)
        if form.is_valid():
            form.save()
            return HttpResponse(status=200)
        else:
            return render(request, 'management/athlete_form.html', {'form': form,'id':id})
    else:
        id = request.GET.get('id',-1)
        if id != -1:
            athlete = Athlete.objects.get(pk=id)
            form = AthleteForm(instance=athlete,session=athlete.team.session.id)
        else:
            form = AthleteForm(session=request.GET.get('session'))
        return render(request, 'management/athlete_form.html', {'form': form,'id':id})

@login_required(login_url='/account/login/admin/')
def athlete_list(request,team_id):
    athletes = Athlete.objects.filter(team__session_id=team_id).order_by('rotation','order')
    context = {
        'athletes':athletes,
    }
    return render(request, 'management/athlete_list.html', context)

@login_required(login_url='/account/login/admin/')
def athlete_delete(request,id):
    Athlete.objects.filter(id=id).delete()
    return HttpResponse(status=200)

@login_required(login_url='/account/login/admin/')
def create_start_lists(request,session_id):
    create_start_List_direct(session_id)
    
    return HttpResponse(status=200)

def create_start_List_direct(session_id):
    session = Session.objects.get(pk=session_id)
    athletes = Athlete.objects.filter(team__session=session).order_by('-rotation','order')
    events = Event.objects.filter(disc=session.competition.disc).order_by('display_order')
    rotations = athletes.values('rotation').distinct()
    rotation_ord = ord('A')
    rotation_list = []
    #athlete_counts = athletes.values('rotation').annotate(total=Count('id'))
    #clear out old
    StartList.objects.filter(session=session).delete()
    for e in events:
        order = 0
        rotation_list.append(chr(rotation_ord)) #add this rotation to list and increment to next rotation letter
        rotation_ord = rotation_ord + 1
        sub_ath = athletes.filter(rotation__in=rotation_list) #get the starting rotations for this event in reverse order
        for ath in sub_ath:
            order = order + 1
            sl = StartList(session=session,event=e,athlete=ath,order=order)
            sl.save()
        sub_ath = athletes.exclude(rotation__in=rotation_list)#now all the rest
        for ath in sub_ath:
            order = order + 1
            sl = StartList(session=session,event=e,athlete=ath,order=order)
            sl.save()

def athlete_update_order(request):
    session = Session.objects.get(pk=request.POST.get('session'))
    aths = request.POST.get('ath_order').split(',')

    for index, val in enumerate(aths,start=1):
        ath = Athlete.objects.get(pk=val)
        ath.order = index
        ath.save()

    return HttpResponse(status=200)


@login_required(login_url='/account/login/admin/')
def setup_cameras(request,id):
    session = Session.objects.get(pk=id)
    context = {
        'title': 'Competition Setup (4/6)',
        'session_name': session.full_name,
        'id':session.id,
    }
    return render(request,'management/setup_cameras.html',context)

@login_required(login_url='/account/login/admin/')
def camera_form(request):
    if request.method == 'POST':
        id = request.POST.get('id','-1')
        if id != '-1':
            cam = Camera.objects.get(pk=id)
            form = CameraForm(request.POST,instance=cam,session=cam.session.id)
        else:
            form = CameraForm(request.POST,session=request.POST.get('session'))
        if form.is_valid():
            form.save()
            return HttpResponse(status=200)
        else:
            return render(request, 'management/camera_form.html', {'form': form,'id':id})
    else:
        id = request.GET.get('id',-1)
        if id != -1:
            cam = Camera.objects.get(pk=id)
            form = CameraForm(instance=cam,session=cam.session.id)
        else:
            form = CameraForm(session=request.GET.get('session'))
        return render(request, 'management/camera_form.html', {'form': form,'id':id})

@login_required(login_url='/account/login/admin/')
def camera_list(request,session_id):
    cameras = Camera.objects.filter(session_id=session_id)
    context = {
        'cameras':cameras,
    }
    return render(request, 'management/camera_list.html', context)

@login_required(login_url='/account/login/admin/')
def camera_delete(request,id):
    Camera.objects.filter(id=id).delete()
    return HttpResponse(status=200)

def cameras_check_missing(request,session_id):
    missed = cameras_check_missing_call(session_id)

    return JsonResponse({'missed':list(missed)})

def cameras_check_missing_call(session_id):
    #see if d1 judge is assigned
    session = Session.objects.get(pk=session_id)
    events = Event.objects.filter(disc=session.competition.disc).order_by('display_order')
    teams = Team.objects.filter(session=session)
    cameras = Camera.objects.filter(session=session)
    missed = []

    for team in teams:
        msg = ""
        for event in events:
            camera = cameras.filter(events=event,teams=team).first()
            if camera == None:
                msg = msg + " " + event.name
            
        if msg != "":
            missed.append(team.name + " missing camera on" + msg)

    return missed

@login_required(login_url='/account/login/admin/')
def setup_sponsors(request,id):
    session = Session.objects.get(pk=id)
    context = {
        'title': 'Competition Setup (5/6)',
        'session_name': session.full_name,
        'id':session.id,
    }
    return render(request,'management/setup_sponsors.html',context)

@login_required(login_url='/account/login/admin/')
def sponsor_form(request):
    if request.method == 'POST':
        id = request.POST.get('id','-1')
        if id != '-1':
            form = SponsorForm(request.POST,request.FILES,instance=Sponsor.objects.get(pk=id))
        else:
            form = SponsorForm(request.POST,request.FILES)
        if form.is_valid():
            form.save()
            return HttpResponse(status=200)
        else:
            return render(request, 'management/sponsor_form.html', {'form': form,'id':id})
    else:
        id = request.GET.get('id',-1)
        if id != -1:
            form = SponsorForm(instance=Sponsor.objects.get(pk=id))
        else:
            form = SponsorForm()
        return render(request, 'management/sponsor_form.html', {'form': form,'id':id})

@login_required(login_url='/account/login/admin/')
def sponsor_list(request,session_id):
    sponsors = Sponsor.objects.filter(session_id=session_id)
    context = {
        'sponsors':sponsors,
    }
    return render(request, 'management/sponsor_list.html', context)

@login_required(login_url='/account/login/admin/')
def sponsor_delete(request,id):
    Sponsor.objects.filter(id=id).delete()
    return HttpResponse(status=200)

@login_required(login_url='/account/login/admin/')
def setup_finish(request,id):
    session = Session.objects.get(pk=id)
    missed_athlete = False
    missed_judge = False
    missed_camera = False
    if len(judges_check_missing_call(id)) > 0:
        missed_judge = True
    if len(cameras_check_missing_call(id)) > 0:
        missed_camera = True
    if Athlete.objects.filter(team__session = session).count() < 1:
        missed_athlete = True
    if missed_camera or missed_athlete or missed_judge:
        setup_complete = False
    else:
        setup_complete = True
    context = {
        'title': 'Competition Setup (6/6)',
        'session_name': session.full_name,
        'id':session.id,
        'missed_athlete':missed_athlete,
        'missed_judge':missed_judge,
        'missed_camera':missed_camera,
        'setup_complete':setup_complete,
    }
    return render(request,'management/setup_finish.html',context)

@login_required(login_url='/account/login/admin/')
def send_session_emails(request,session_id):
    if len(StartList.objects.filter(session_id=session_id)) <= 0:
        create_start_List_direct(session_id)
    judges = Judge.objects.filter(session_id=session_id)
    cameras = Camera.objects.filter(session_id=session_id)
    teams = Team.objects.filter(session_id=session_id)
    session = Session.objects.get(pk=session_id)
    messages = []
    app.views.setup_firebase_managers(session)
    
    for judge in judges:
        if judge.d1_email != None and judge.d1_email != '':
            messages.append(build_judge_notice(session,judge.event.full_name,judge.d1,judge.d1_email,judge.d1_password,'D1'))
        if judge.d2_email != None and judge.d2_email != '':
            messages.append(build_judge_notice(session,judge.event.full_name,judge.d2,judge.d2_email,judge.d2_password,'D2'))
        if judge.e1_email != None and judge.e1_email != '':
            messages.append(build_judge_notice(session,judge.event.full_name,judge.e1,judge.e1_email,judge.e1_password,'E1'))
        if judge.e2_email != None and judge.e2_email != '':
            messages.append(build_judge_notice(session,judge.event.full_name,judge.e2,judge.e2_email,judge.e2_password,'E2'))
        if judge.e3_email != None and judge.e3_email != '':
            messages.append(build_judge_notice(session,judge.event.full_name,judge.e3,judge.e3_email,judge.e3_password,'E3'))
        if judge.e4_email != None and judge.e4_email != '':
            messages.append(build_judge_notice(session,judge.event.full_name,judge.e4,judge.e4_email,judge.e4_password,'E4'))


    for camera in cameras:
        if camera.email != None and camera.email != '':
            messages.append(build_camera_notice(session,camera))

    for team in teams:
        if team.head_coach_email != None and team.head_coach_email != '':
            messages.append(build_coach_notice(session,team))

    send_mass_html_mail(messages)
    
    return HttpResponse(status=200)

def build_judge_notice(session,event,name,email,password,type):
    reqs = []
    reqs.append("An internet connection - broadband wired or wireless (3G or 4G/LTE)")
    reqs.append("5Mbps (up/down) bandwidth")
    reqs.append("Google Chrome 46+")
    reqs.append("8 Gb or higher RAM")
    context = {
        'name': name,
        'email': email,
        'password': password,
        'session': session,
        'assigned': 'to judge',
        'assigned_full': type + ' Judge on ' + event,
        'url_extra':'/account/login_judge',
        'reqs':reqs
    }
    html_message = render_to_string('management/email_notice.html', context)
    plain_message = strip_tags(html_message)
    subject = str(type) + " Judge Login for " + str(session.full_name())
    #message = "You will be the " + str(type) + " judge for " + str(session.full_name()) + " on " + session.competition.date.strftime('%Y-%m-%d') + " " + str(session.time) +"<br/>"
    #message += "Login at <a href='https://www.stslivegym.com'>https://www.stslivegym.com</a> with:<br/>"
    #message += "Email: " + str(email) + "<br/>Password: " + str(password)
    test = ('test','test')
    message = (subject, plain_message, html_message, 'noreply@stslivegym.com', [email])
    return message

def build_camera_notice(session,camera):
    reqs = []
    reqs.append("A wired internet connection")
    reqs.append("20 Mbps (up/down) bandwidth")
    reqs.append("Iphone IOS 13+, Android 9+, Windows 8.1+ with Chrome 46+")
    reqs.append("Camera and microphone access allowed in settings")
    teams = ""
    events = ""
    for t in camera.teams.all():
        teams = teams + ", " + t.abbreviation
    for e in camera.events.all():
        events = events + ", " + e.name 
    context = {
        'name': camera.name,
        'email': camera.email,
        'password': camera.password,
        'session': session,
        'assigned': 'to operate a camera for',
        'assigned_full': 'Camera Operator for' + teams[1:] + " on" + events[1:],
        'url_extra':'/account/login_camera',
        'reqs':reqs
    }
    html_message = render_to_string('management/email_notice.html', context)
    plain_message = strip_tags(html_message)
    subject = "Camera Login for " + str(session.full_name())
    #message = "You will be the " + str(type) + " judge for " + str(session.full_name()) + " on " + session.competition.date.strftime('%Y-%m-%d') + " " + str(session.time) +"<br/>"
    #message += "Login at <a href='https://www.stslivegym.com'>https://www.stslivegym.com</a> with:<br/>"
    #message += "Email: " + str(email) + "<br/>Password: " + str(password)
    test = ('test','test')
    message = (subject, plain_message, html_message, 'noreply@stslivegym.com', [camera.email])
    return message

def build_coach_notice(session,team):
    reqs = []
    reqs.append("An internet connection - broadband wired or wireless (3G or 4G/LTE)")
    reqs.append("2.5Mbps (up/down) bandwidth")
    reqs.append("Google Chrome 46+")
    context = {
        'name': team.name,
        'email': team.head_coach_email,
        'password': team.coach_password,
        'session': session,
        'assigned': 'to coach',
        'assigned_full': 'Coach for ' + team.name,
        'url_extra':'/account/login_coach',
        'reqs':reqs
    }
    html_message = render_to_string('management/email_notice.html', context)
    plain_message = strip_tags(html_message)
    subject = "Coach Login for " + str(session.full_name())
    #message = "You will be the " + str(type) + " judge for " + str(session.full_name()) + " on " + session.competition.date.strftime('%Y-%m-%d') + " " + str(session.time) +"<br/>"
    #message += "Login at <a href='https://www.stslivegym.com'>https://www.stslivegym.com</a> with:<br/>"
    #message += "Email: " + str(email) + "<br/>Password: " + str(password)
    test = ('test','test')
    message = (subject, plain_message, html_message, 'noreply@stslivegym.com', [team.head_coach_email])
    return message

def send_mass_html_mail(datatuple, fail_silently=False, user=None, password=None, 
                        connection=None):
    """
    Given a datatuple of (subject, text_content, html_content, from_email,
    recipient_list), sends each message to each recipient list. Returns the
    number of emails sent.

    If from_email is None, the DEFAULT_FROM_EMAIL setting is used.
    If auth_user and auth_password are set, they're used to log in.
    If auth_user is None, the EMAIL_HOST_USER setting is used.
    If auth_password is None, the EMAIL_HOST_PASSWORD setting is used.

    """
    connection = connection or get_connection(
        username=user, password=password, fail_silently=fail_silently)
    messages = []
    for subject, text, html, from_email, recipient in datatuple:
        message = EmailMultiAlternatives(subject, text, from_email, recipient)
        message.attach_alternative(html, 'text/html')
        messages.append(message)
    return connection.send_messages(messages)

def email_test(request):
    session = Session.objects.all().first()
    judge = Judge.objects.filter(session=session).first()
    reqs = []
    reqs.append("An internet connection - broadband wired or wireless (3G or 4G/LTE)")
    reqs.append("2.5Mbps (up/down) bandwidth")
    reqs.append("Google Chrome 46+")
    reqs.append("8 Gb or higher RAM")
    
    context = {
        'name': judge.d1,
        'email': judge.d1_email,
        'password': judge.d1_password,
        'session': session,
        'assigned': 'to judge',
        'assigned_full': 'D1 Judge on ' + judge.event.full_name,
        'url_extra':'/account/login_judge',
        'reqs':reqs
    }
    return render(request,'management/email_notice.html',context)

def judges_get(request):
    comp = request.GET.get('comp')
    disc = request.GET.get('disc')
    event = request.GET.get('event')
    judge = Judge.objects.filter(competition_id=comp,disc=disc,event=event)
    return JsonResponse({'judges':list(judge.values())})

def judges_update(request):
    comp = request.POST.get('comp')
    disc = request.POST.get('disc')
    event = request.POST.get('event')
    compInstance = Competition.objects.get(pk=comp)
    judge, created = Judge.objects.update_or_create(
        competition=comp,disc=disc,event=event,
        defaults={'competition': compInstance,'disc':disc,'event':event, 'd1':request.POST.get('d1'),'d1_affil':request.POST.get('d1_affil'),
                  'd2':request.POST.get('d2',''),'d2_affil':request.POST.get('d2_affil',''),'e1':request.POST.get('e1'),'e1_affil':request.POST.get('e1_affil'),
                  'e2':request.POST.get('e2'),'e2_affil':request.POST.get('e2_affil'),'e3':request.POST.get('e3'),'e3_affil':request.POST.get('e3_affil'),
                  'e4':request.POST.get('e4'),'e4_affil':request.POST.get('e4_affil')},
    )
    resp = {'updated':True}
    return JsonResponse(resp)



def athlete_create_update(request):
    athleteid = request.GET.get('id','-1')
    if athleteid != '-1':
        #update
        ath = Athlete.objects.get(pk=athleteid)
        ath.name =request.GET.get('name','')
        ath.level =request.GET.get('level','')
        ath.team =request.GET.get('team','')
        ath.save()
    else:
        ath = Athlete(name=request.GET.get('name',''),level =request.GET.get('level',''),team =request.GET.get('team',''),competition_id=request.GET.get('comp'),disc=request.GET.get('disc'))
        ath.save()
    return HttpResponse(status=200)

def athlete_manage(request):
    athid = request.GET.get('id',-1)
    if athid != -1:
        ath = Athlete.objects.get(pk=athid)
        manage_type = "save"
    else:
        ath = ""
        manage_type="add"

    context = {
        'id':athid,
        'type':manage_type,
        'ath':ath
    }
    return render(request, 'management/athlete_manage.html', context)

def session_manage(request):
    id = request.GET.get('id',-1)
    name = ""
    time = ""
    if id != -1:
        session = Session.objects.get(pk=id)
        name = session.name
        time = session.time
        manage_type = "save"
    else:
        manage_type="add"

    context = {
        'id':id,
        'type':manage_type,
        'name':name,
        'time':time,
    }
    return render(request, 'management/session_manage.html', context)

def session_create_update(request):
    id = request.GET.get('id','-1')
    if id != '-1':
        #update
        session = Session.objects.get(pk=id)
        session.name=request.GET.get('name','')
        session.time=request.GET.get('time')
        session.competition_id = request.GET.get('comp_id')
        session.save()
    else:
        session = Session(name=request.GET.get('name',''),time=request.GET.get('time'),competition_id=request.GET.get('comp_id'))
        session.save()
    return HttpResponse(status=200)

def competition_manage(request):
    compid = request.GET.get('id',-1)
    name = ""
    date = datetime.now().date()
    comp_type = ""
    if compid != -1:
        comp = Competition.objects.get(pk=compid)
        name = comp.name
        date = comp.date
        comp_type = comp.type
        manage_type = "save"
    else:
        manage_type="add"

    context = {
        'id':compid,
        'type':manage_type,
        'comp_type':comp_type,
        'name':name,
        'date':date.strftime("%Y-%m-%d"),
        'types':Competition.COMPETITION_TYPE
    }
    return render(request, 'management/competition_manage.html', context)

def competition_create_update(request):
    compid = request.GET.get('id','-1')
    if compid != '-1':
        #update
        comp = Competition.objects.get(pk=compid)
        comp.name=request.GET.get('name','')
        comp.type=request.GET.get('type','T')
        comp.date=request.GET.get('date')
        comp.disc=request.GET.get('disc')
        comp.save()
    else:
        comp = Competition(name=request.GET.get('name',''),type=request.GET.get('type','T'),date=request.GET.get('date'),disc=request.GET.get('disc'))
        comp.save()
    return HttpResponse(status=200)
