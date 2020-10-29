from django.shortcuts import render,redirect
from .models import User
from .forms import SignUpForm,LoginForm,EmailPasswordForm
from django.contrib.auth import authenticate, login
from management.models import Judge,Camera,Session,Competition,Team
import datetime

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password1')
            user = authenticate(request, email=email, password=password)
            login(request, user)
            #now create the stripe customer
            return redirect('/management/setup_competition/')
    else:
        form = SignUpForm()
    return render(request, 'account/signup.html', {'form': form})

def login_admin(request):
    if request.method == 'POST':
        login_form = LoginForm(data=request.POST)
        if login_form.is_valid():
            email = login_form.cleaned_data.get('email')
            raw_password = login_form.cleaned_data.get('password')
            user = authenticate(request, email=email, password=raw_password)
            login(request, user)
            return redirect('/management/setup_competition/')
    else:
        login_form = LoginForm()

    context = {
        'form': login_form,
    }
    return render(request, 'account/login.html', context)

def login_judge(request):
    err = ''
    if request.method == 'POST':
        login_form = EmailPasswordForm(data=request.POST)
        if login_form.is_valid():
            email = login_form.cleaned_data.get('email')
            password = login_form.cleaned_data.get('password')
            type = None
            judges = Judge.objects.filter(session__competition__date__gte= datetime.datetime.now() -  datetime.timedelta(days=2)) #got possible judges
            if len(judges) > 0:
                if len(judges.filter(d1_email=email,d1_password=password)) > 0:
                    type='d1'
                    judge = judges.filter(d1_email=email,d1_password=password).first()
                    name = judge.d1
                    event = judge.event
                    session = judge.session
                elif len(judges.filter(d2_email=email,d2_password=password)) > 0:
                    type='d2'
                    judge = judges.filter(d2_email=email,d2_password=password).first()
                    name = judge.d2
                    event = judge.event
                    session = judge.session
                elif len(judges.filter(e1_email=email,e1_password=password)) > 0:
                    type='e1'
                    judge = judges.filter(e1_email=email,e1_password=password).first()
                    name = judge.e1
                    event = judge.event
                    session = judge.session
                    ej = 1
                elif len(judges.filter(e2_email=email,e2_password=password)) > 0:
                    type='e2'
                    judge = judges.filter(e2_email=email,e2_password=password).first()
                    name = judge.e2
                    event = judge.event
                    session = judge.session
                    ej = 2
                elif len(judges.filter(e3_email=email,e3_password=password)) > 0:
                    type='e3'
                    judge = judges.filter(e3_email=email,e3_password=password).first()
                    name = judge.e3
                    event = judge.event
                    session = judge.session
                    ej = 3
                elif len(judges.filter(e4_email=email,e4_password=password)) > 0:
                    type='e4'
                    judge = judges.filter(e4_email=email,e4_password=password).first()
                    name = judge.e4
                    event = judge.event
                    session = judge.session
                    ej = 4
                if type != None:
                    request.session['session'] = session.id
                    request.session['event'] = event.name
                    request.session['disc'] = session.competition.disc.name
                    request.session['name'] = name
                    request.session['email'] = email
                    request.session['type'] = type
                    request.session.set_expiry(0)#until they close browser
                    if type[0:1] == 'e':
                        request.session['ej'] = ej
                        return redirect('/ejudge_select/')
                    else:
                        return redirect('/d1/')
 
            err = "Incorrect Login Inforation"
    else:
        login_form = EmailPasswordForm()

    context = {
        'form': login_form,
        'err':err,
        'type':'Judge',
    }
    return render(request, 'account/login_simple.html', context)

def login_camera(request):
    err = ''
    if request.method == 'POST':
        login_form = EmailPasswordForm(data=request.POST)
        if login_form.is_valid():
            email = login_form.cleaned_data.get('email')
            password = login_form.cleaned_data.get('password')
            type = None
            cameras = Camera.objects.filter(session__competition__date__gte= datetime.datetime.now() -  datetime.timedelta(days=2)) #got possible cameras
            if len(cameras) > 0:
                camera = cameras.filter(email=email,password=password)
                if len(camera) > 0:
                    camera = camera.first()
                    request.session['session'] = camera.session.id
                    request.session['camera'] = camera.id
                    request.session['type'] = 'camera'
                    request.session['disc'] = camera.session.competition.disc.name
                    request.session.set_expiry(0)#until they close browser
                    return redirect('/streaming/camera/')
 
            err = "Incorrect Login Inforation"
    else:
        login_form = EmailPasswordForm()

    context = {
        'form': login_form,
        'err':err,
        'type':'Camera',
    }
    return render(request, 'account/login_simple.html', context)

def login_coach(request):
    err = ''
    if request.method == 'POST':
        login_form = EmailPasswordForm(data=request.POST)
        if login_form.is_valid():
            email = login_form.cleaned_data.get('email')
            password = login_form.cleaned_data.get('password')
            type = None
            teams = Team.objects.filter(session__competition__date__gte= datetime.datetime.now() -  datetime.timedelta(days=2)) #got possible teams
            if len(teams) > 0:
                coach = teams.filter(head_coach_email=email,coach_password=password)
                if len(coach) > 0:
                    coach = coach.first()
                    request.session['session'] = teams.session.id
                    request.session['team'] = team.id
                    request.session['type'] = 'coach'
                    request.session['disc'] = teams.session.competition.disc.name
                    request.session.set_expiry(0)#until they close browser
                    return redirect('/coach/')
 
            err = "Incorrect Login Inforation"
    else:
        login_form = EmailPasswordForm()

    context = {
        'form': login_form,
        'err':err,
        'type':'Coach',
    }
    return render(request, 'account/login_simple.html', context)