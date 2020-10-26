from django.shortcuts import render,redirect
from django.http import HttpRequest,JsonResponse,HttpResponse
from django.template import RequestContext
from datetime import datetime
from .forms import CompetitionForm,SessionForm,JudgeForm,TeamForm,AthleteForm,CameraForm,SponsorForm
from .models import Competition,Session,Athlete,Judge,Team,Disc,Event,Camera,Sponsor
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required,user_passes_test

# Create your views here.
@login_required(login_url='/account/login/')
def setup_competition(request):

    context = {
        'title': 'Compeition Setup (1/6)',
        'discs': Disc.objects.all(),
    }
    return render(request,'management/setup_competition.html',context)

def competition_list(request):
    comps = Competition.objects.filter(disc=request.GET.get('disc'),admin=request.user)

    context = {
        'comps':comps,
    }
    return render(request, 'management/competition_list.html', context)

@login_required(login_url='/account/login/')
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

@login_required(login_url='/account/login/')
def competition_delete(request):
    Competition.objects.filter(id=request.GET.get('id')).delete()
    return HttpResponse(status=200)

@login_required(login_url='/account/login/')
def session_list(request):
    sessions = Session.objects.filter(competition_id=request.GET.get('comp'))

    context = {
        'sessions':sessions,
    }
    return render(request, 'management/session_list.html', context)

@login_required(login_url='/account/login/')
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

@login_required(login_url='/account/login/')
def session_delete(request):
    Session.objects.filter(id=request.GET.get('id')).delete()
    return HttpResponse(status=200)

@login_required(login_url='/account/login/')
def setup_judges(request,id):
    session = Session.objects.get(pk=id)
    events = Event.objects.filter(disc=session.competition.disc)
   
    context = {
        'title': 'Compeition Setup (2/6)',
        'session_name': session.full_name,
        'events':events,
        'id':session.id,
    }
    return render(request,'management/setup_judges.html',context)

@login_required(login_url='/account/login/')
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

@login_required(login_url='/account/login/')
def setup_athletes(request,id):
    session = Session.objects.get(pk=id)
    context = {
        'title': 'Compeition Setup (3/6)',
        'session_name': session.full_name,
        'id':session.id,
    }
    return render(request,'management/setup_athletes.html',context)

@login_required(login_url='/account/login/')
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

@login_required(login_url='/account/login/')
def team_list(request,session_id):
    teams = Team.objects.filter(session_id=session_id)
    context = {
        'teams':teams,
    }
    return render(request, 'management/team_list.html', context)

@login_required(login_url='/account/login/')
def team_delete(request,id):
    Team.objects.filter(id=id).delete()
    return HttpResponse(status=200)

@login_required(login_url='/account/login/')
def athlete_form(request):
    if request.method == 'POST':
        id = request.POST.get('id','-1')
        if id != '-1':
            form = AthleteForm(request.POST,instance=Athlete.objects.get(pk=id))
        else:
            form = AthleteForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponse(status=200)
        else:
            return render(request, 'management/athlete_form.html', {'form': form,'id':id})
    else:
        id = request.GET.get('id',-1)
        if id != -1:
            form = AthleteForm(instance=Athlete.objects.get(pk=id))
        else:
            form = AthleteForm()
        return render(request, 'management/athlete_form.html', {'form': form,'id':id})

@login_required(login_url='/account/login/')
def athlete_list(request,team_id):
    athletes = Athlete.objects.filter(team_id=team_id)
    context = {
        'athletes':athletes,
    }
    return render(request, 'management/athlete_list.html', context)

@login_required(login_url='/account/login/')
def athlete_delete(request,id):
    Athlete.objects.filter(id=id).delete()
    return HttpResponse(status=200)

@login_required(login_url='/account/login/')
def setup_cameras(request,id):
    session = Session.objects.get(pk=id)
    context = {
        'title': 'Compeition Setup (4/6)',
        'session_name': session.full_name,
        'id':session.id,
    }
    return render(request,'management/setup_cameras.html',context)

@login_required(login_url='/account/login/')
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

@login_required(login_url='/account/login/')
def camera_list(request,session_id):
    cameras = Camera.objects.filter(session_id=session_id)
    context = {
        'cameras':cameras,
    }
    return render(request, 'management/camera_list.html', context)

@login_required(login_url='/account/login/')
def camera_delete(request,id):
    Camera.objects.filter(id=id).delete()
    return HttpResponse(status=200)

@login_required(login_url='/account/login/')
def setup_sponsors(request,id):
    session = Session.objects.get(pk=id)
    context = {
        'title': 'Compeition Setup (5/6)',
        'session_name': session.full_name,
        'id':session.id,
    }
    return render(request,'management/setup_sponsors.html',context)

@login_required(login_url='/account/login/')
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

@login_required(login_url='/account/login/')
def sponsor_list(request,session_id):
    sponsors = Sponsor.objects.filter(session_id=session_id)
    context = {
        'sponsors':sponsors,
    }
    return render(request, 'management/sponsor_list.html', context)

@login_required(login_url='/account/login/')
def sponsor_delete(request,id):
    Sponsor.objects.filter(id=id).delete()
    return HttpResponse(status=200)

@login_required(login_url='/account/login/')
def setup_finish(request,id):
    session = Session.objects.get(pk=id)
    context = {
        'title': 'Compeition Setup (6/6)',
        'session_name': session.full_name,
        'id':session.id,
    }
    return render(request,'management/setup_finish.html',context)

@login_required(login_url='/account/login/')
def send_session_emails(request,session_id):
    judges = Judge.objects.filter(session_id=session_id)
    cameras = Camera.objects.filter(session_id=session_id)
    session = Session.objects.get(pk=session_id)
    
    for judge in judges:
        if judge.d1_email != None and judge.d1_email != '':
            send_judge_notice(session,judge.d1_email,judge.d1_password,'D1')
        if judge.d2_email != None and judge.d2_email != '':
            send_judge_notice(session,judge.d2_email,judge.d2_password,'D2')
        if judge.e1_email != None and judge.e1_email != '':
            send_judge_notice(session,judge.e1_email,judge.e1_password,'E1')
        if judge.e2_email != None and judge.e2_email != '':
            send_judge_notice(session,judge.e2_email,judge.e2_password,'E2')
        if judge.e3_email != None and judge.e3_email != '':
            send_judge_notice(session,judge.e3_email,judge.e3_password,'E3')
        if judge.e4_email != None and judge.e4_email != '':
            send_judge_notice(session,judge.e4_email,judge.e4_password,'E4')

    for camera in cameras:
        if camera.email != None and camera.email != '':
            send_camera_notice(session,camera)
    
    return HttpResponse(status=200)

def send_judge_notice(session,email,password,type):
    subject = "Judge " + str(type) + " Login for " + str(session.full_name())
    message = "You will be the " + str(type) + " judge for " + str(session.full_name()) + " on " + session.competition.date.strftime('%Y-%m-%d') + " " + str(session.time) +"<br/>"
    message += "Login at <a href='https://www.stslivegym.com'>https://www.stslivegym.com</a> with:<br/>"
    message += "Email: " + str(email) + "<br/>Password: " + str(password)
    send_mail(subject, message, 'noreply@stslivegym.com', [email],html_message=message)

def send_camera_notice(session,camera):
    subject = "Camera Login for " + str(session.full_name())
    message = "You will be a camera operator for " + str(session.full_name()) + " on " + session.competition.date.strftime('%Y-%m-%d') + " " + str(session.time) +"<br/>"
    message += "Login at <a href='https://www.stslivegym.com'>https://www.stslivegym.com</a> with:<br/>"
    message += "Email: " + str(camera.email) + "<br/>Password: " + str(camera.password)
    send_mail(subject, message, 'noreply@stslivegym.com', [camera.email],html_message=message)

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
