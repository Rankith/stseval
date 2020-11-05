from django.shortcuts import render,redirect
from .models import User
from .forms import SignUpForm,LoginForm,EmailPasswordForm
from django.contrib.auth import authenticate, login
from management.models import Judge,Camera,Session,Competition,Team
import datetime
from django.db.models import Q

def signup(request,type='spectator'):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password1')
            user = authenticate(request, email=email, password=password)
            login(request, user)
            #now create the stripe customer
            if type == "admin":
                return redirect('/management/setup_competition/')
            else:
                return redirect('/select_session/')
    else:
        form = SignUpForm()
    return render(request, 'account/signup.html', {'form': form})

def login_admin(request,type='spectator'):
    err = ''
    if request.method == 'POST':
        login_form = LoginForm(data=request.POST)
        if login_form.is_valid():
            email = login_form.cleaned_data.get('email')
            raw_password = login_form.cleaned_data.get('password')
            user = authenticate(request, email=email, password=raw_password)
            if user is not None:
                login(request, user,backend='django.contrib.auth.backends.ModelBackend')
                if type == "admin":
                    return redirect('/management/setup_competition/')
                else:
                    return redirect('/select_session/')
            else:
                err = "Incorrect Login Inforation"
    else:
        login_form = LoginForm()

    context = {
        'form': login_form,
        'err':err,
        'type':type,
    }
    return render(request, 'account/login.html', context)

def login_multiple(request,type,sub_type,id):
    email = request.GET.get('email')
    password = request.GET.get('password')
    if type=='judge':
        judge = Judge.objects.get(pk=id)
        if sub_type == 'D1' and judge.d1_email == email and judge.d1_password == password:
            jt = 'D1'
            name = judge.d1
            ej=0
        if sub_type == 'D2' and judge.d2_email == email and judge.d2_password == password:
            jt = 'D2'
            name = judge.d2
            ej=0
        if sub_type == 'E1' and judge.e1_email == email and judge.e1_password == password:
            jt = 'E1'
            name = judge.e1
            ej=1
        if sub_type == 'E2' and judge.e2_email == email and judge.e2_password == password:
            jt = 'E2'
            name = judge.e2
            ej=2
        if sub_type == 'E3' and judge.e3_email == email and judge.e3_password == password:
            jt = 'E3'
            name = judge.e3
            ej=3
        if sub_type == 'E4' and judge.e4_email == email and judge.e4_password == password:
            jt = 'E4'
            name = judge.e4
            ej=4
        if jt != None:
            return login_judge_do(request,judge.session,judge.event,name,email,jt,ej)
        else:
            return redirect('/')
    elif type=='coach':
        coach = Team.objects.get(pk=id)
        if coach.head_coach_email == email and coach.coach_password == password:
            return login_coach_do(request,coach.session,coach)
        else:
            return redirect('/')
    elif type=='camera':
        camera = Camera.objects.get(pk=id)
        if camera.email == email and camera.password == password:
            return login_camera_do(request,camera)
        else:
            return redirect('/')

def login_camera_do(request,camera):
    request.session['session'] = camera.session.id
    request.session['camera'] = camera.id
    request.session['type'] = 'camera'
    request.session['disc'] = camera.session.competition.disc.name
    request.session.set_expiry(0)#until they close browser
    return redirect('/streaming/camera/')

def login_coach_do(request,session,team):
    request.session['session'] = session.id
    request.session['team'] = team.id
    request.session['disc'] = session.competition.disc.name
    request.session['type'] = 'coach'
    request.session.set_expiry(0)#until they close browser
    return redirect('/coach/')          

def login_judge_do(request,session,event,name,email,jt,ej):
    request.session['session'] = session.id
    request.session['event'] = event.name
    request.session['disc'] = session.competition.disc.name
    request.session['name'] = name
    request.session['email'] = email
    request.session['type'] = jt.lower()
    request.session.set_expiry(0)#until they close browser
    if jt[0:1] == 'E':
        request.session['ej'] = ej
        return redirect('/ejudge_select/')
    else:
        return redirect('/d1/')

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
                judges = judges.filter(Q(d1_email=email,d1_password=password) | Q(d2_email=email,d2_password=password) | Q(e1_email=email,e1_password=password) | Q(e2_email=email,e2_password=password) | Q(e3_email=email,e3_password=password) | Q(e4_email=email,e4_password=password))
                possibles = []
                for judge in judges:
                    if judge.d1_email == email and judge.d1_password == password:
                        p = {}
                        name = judge.d1
                        p['type'] = 'D1'
                        p['display'] = judge.session.full_name() + ": " + judge.event.name + " " + p['type']
                        p['id'] = judge.id
                        ej = 0
                        possibles.append(p)
                    if judge.d2_email == email and judge.d2_password == password:
                        p = {}
                        name = judge.d2
                        p['type'] = 'D2'
                        p['display'] = judge.session.full_name() + ": " + judge.event.name + " " + p['type']
                        p['id'] = judge.id
                        ej = 0
                        possibles.append(p)
                    if judge.e1_email == email and judge.e1_password == password:
                        p = {}
                        name = judge.e1
                        p['type'] = 'E1'
                        p['display'] = judge.session.full_name() + ": " + judge.event.name + " " + p['type']
                        p['id'] = judge.id
                        ej = 1
                        possibles.append(p)
                    if judge.e2_email == email and judge.e2_password == password:
                        p = {}
                        name = judge.e2
                        p['type'] = 'E2'
                        p['display'] = judge.session.full_name() + ": " + judge.event.name + " " + p['type']
                        p['id'] = judge.id
                        ej = 2
                        possibles.append(p)
                    if judge.e3_email == email and judge.e3_password == password:
                        p = {}
                        name = judge.e3
                        p['type'] = 'E3'
                        p['display'] = judge.session.full_name() + ": " + judge.event.name + " " + p['type']
                        p['id'] = judge.id
                        ej = 3
                        possibles.append(p)
                    if judge.e4_email == email and judge.e4_password == password:
                        p = {}
                        name = judge.e4
                        p['type'] = 'E4'
                        p['display'] = judge.session.full_name() + ": " + judge.event.name + " " + p['type']
                        p['id'] = judge.id
                        ej = 4
                        possibles.append(p)
                if len(possibles) > 0:
                    if len(possibles) == 1:
                        judge = Judge.objects.get(pk=possibles[0]['id'])
                        return login_judge_do(request,judge.session,judge.event,name,email,possibles[0]['type'],ej)
                    else:
                        #more then one
                        context = {
                            'possibles': possibles,
                            'email':email,
                            'password':password,
                            'type':'judge',
                        }
                        return render(request, 'account/login_multiple.html', context)
                else:
                    err = "Incorrect Login Inforation"
            else:
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
                if len(camera) == 1:
                    camera = camera.first()
                    return login_camera_do(request,camera)
                elif len(camera) > 1:
                    possibles = []
                    for cam in camera:
                        p = {}
                        p['type'] = 'camera'
                        p['id'] = cam.id
                        p['display'] = cam.session.full_name() + ": " + cam.name
                        possibles.append(p)
                    #more then one
                    context = {
                        'possibles': possibles,
                        'email':email,
                        'password':password,
                        'type':'camera',
                    }
                    return render(request, 'account/login_multiple.html', context)
 
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
                if len(coach) == 1:
                    coach = coach.first()
                    return login_coach_do(request,coach.session,coach)
                elif len(coach) > 1:
                    possibles = []
                    for c in coach:
                        p = {}
                        p['type'] = 'coach'
                        p['id'] = c.id
                        p['display'] = c.session.full_name() + ": " + c.name
                        possibles.append(p)
                    #more then one
                    context = {
                        'possibles': possibles,
                        'email':email,
                        'password':password,
                        'type':'coach',
                    }
                    return render(request, 'account/login_multiple.html', context)
 
            err = "Incorrect Login Inforation"
    else:
        login_form = EmailPasswordForm()

    context = {
        'form': login_form,
        'err':err,
        'type':'Coach',
    }
    return render(request, 'account/login_simple.html', context)