from django.shortcuts import render,redirect
from .models import User
from .forms import SignUpForm,LoginForm,EmailPasswordForm
from django.contrib.auth import authenticate, login
from management.models import Judge,Camera,Session,Competition,Team
import datetime
from django.db.models import Q, F, Sum, Count
import stripe
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from account.models import Purchase
from account import stripe_handler
from django.contrib.auth.decorators import login_required,user_passes_test
import csv

def signup(request,type='spectator'):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password1')
            user = authenticate(request, email=email, password=password)
            check_create_stripe_user(user)
            login(request, user)
            request.session['type'] = type
            #now create the stripe customer
            if type == "admin":
                return redirect('/management/setup_competition/')
            else:
                next = request.GET.get('next','/select_session/')
                return redirect(next)

    else:
        form = SignUpForm()
    return render(request, 'account/signup.html', {'form': form})

def check_create_stripe_user(user):
    if settings.STRIPE_TEST_MODE:
        stripe.api_key = settings.STRIPE_API_KEY_TEST
    else:
        stripe.api_key = settings.STRIPE_API_KEY
    if user.stripe_customer == '':
        customer = stripe.Customer.create(email=user.email)
        user.stripe_customer = customer.id
        user.save()

def login_admin(request,type='spectator'):
    err = ''
    if request.method == 'POST':
        login_form = LoginForm(data=request.POST)
        if login_form.is_valid():
            email = login_form.cleaned_data.get('email')
            raw_password = login_form.cleaned_data.get('password')
            user = authenticate(request, email=email, password=raw_password)
            if user is not None:
                check_create_stripe_user(user)
                login(request, user,backend='django.contrib.auth.backends.ModelBackend')
                request.session['type'] = request.session.get('type','') + ',' + type
                request.session['email'] = email
                
                #request.session['chat_name'] = user.first_name + " " + user.last_name
                if type == "admin":
                    request.session['chat_name'] = "Meet Administrator"
                    request.session['backup_video_manage'] = True
                    return redirect('/management/setup_competition/')
                else:
                    next = request.GET.get('next','/select_session/')
                    return redirect(next)
            else:
                err = "Incorrect Login Information.  Make sure you selected the correct login"
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
    request.session['type'] = request.session.get('type','') + ',' +  'camera'
    request.session['disc'] = camera.session.competition.disc.name
    request.session['email'] = camera.email
    request.session['chat_name'] = 'Camera - ' + camera.name
    request.session.set_expiry(0)#until they close browser
    return redirect('/streaming/camera/')

def login_coach_do(request,session,team):
    request.session['session'] = session.id
    request.session['team'] = team.id
    request.session['disc'] = session.competition.disc.name
    request.session['email'] = team.head_coach_email
    request.session['type'] = request.session.get('type','') + ',' + 'coach'
    request.session['chat_name'] = 'Coach - ' + team.abbreviation
    request.session['backup_video_manage'] = True
    request.session.set_expiry(0)#until they close browser
    return redirect('/coach/')          

def login_judge_do(request,session,event,name,email,jt,ej):
    request.session['session'] = session.id
    request.session['event'] = event.name
    request.session['disc'] = session.competition.disc.name
    request.session['name'] = name
    request.session['email'] = email
    request.session['type'] = request.session.get('type','') + ',' + jt.lower()
   
    request.session.set_expiry(0)#until they close browser
    if jt[0:1] == 'E':
        request.session['ej'] = ej
        request.session['chat_name'] = event.name + " " + jt + " - " + name
        return redirect('/ejudge_select/')
    else:#D
        if jt == 'D2' and session.competition.disc.name == "WAG" and (session.level == Session.WDP or session.level == Session.NCAA): #d2_wag version
            request.session['chat_name'] = event.name + " D2 - " + name
            return redirect('/d2_wag/')
        else:
            request.session['chat_name'] = event.name + " D1 - " + name
            return redirect('/d1/')

def login_judge(request):
    err = ''
    if request.method == 'POST':
        login_form = EmailPasswordForm(data=request.POST)
        if login_form.is_valid():
            email = login_form.cleaned_data.get('email')
            password = login_form.cleaned_data.get('password')
            type = None
            judges = Judge.objects.filter((Q(session__competition__date__gte=datetime.datetime.now() - datetime.timedelta(days=3)) | Q(session__test=True)) & Q(session__active=True)) #got possible judges
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
                    err = "Incorrect Login Information.  Make sure you selected the correct login"
            else:
                err = "Incorrect Login Information.  Make sure you selected the correct login"
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
            cameras = Camera.objects.filter((Q(session__competition__date__gte=datetime.datetime.now() - datetime.timedelta(days=1)) | Q(session__test=True)) & Q(session__active=True))  #got possible cameras
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
 
            err = "Incorrect Login Information.  Make sure you selected the correct login"
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
            teams = Team.objects.filter((Q(session__competition__date__gte=datetime.datetime.now() - datetime.timedelta(days=3)) | Q(session__test=True)) & Q(session__active=True))  #got possible teams
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
 
            err = "Incorrect Login Information.  Make sure you selected the correct login"
    else:
        login_form = EmailPasswordForm()

    context = {
        'form': login_form,
        'err':err,
        'type':'Coach',
    }
    return render(request, 'account/login_simple.html', context)

def check_session_access_direct(user,session_id):
    session = Session.objects.get(pk=session_id)
    if user.is_staff or user.is_superuser or session.free:
        return "Yes"
    if user.sessions_available.filter(id=session_id).exists():
        return "Yes"
    else:
        #now check for emails
        if session.competition.admin == user:
            user.sessions_available.add(session)
            return "Yes"
        elif len(Team.objects.filter(session=session,head_coach_email=user.email)) > 0:
            user.sessions_available.add(session)
            return "Yes"
        elif len(Judge.objects.filter(Q(session=session) & (Q(d1_email=user.email) | Q(d2_email=user.email) | Q(e1_email=user.email) | Q(e2_email=user.email) | Q(e3_email=user.email) | Q(e4_email=user.email)))) > 0:
            user.sessions_available.add(session)
            return "Yes"
        return "No"

@login_required(login_url='/account/login/admin/')
def check_session_access(request,session_id):
   return HttpResponse(check_session_access_direct(request.user,session_id))

@login_required(login_url='/account/login/admin/')
def earnings(request):
    connect_status = stripe_handler.check_account_status(request.user)
    account = None
    if connect_status == "complete":
        #now check for things they may need soon
        account = stripe_handler.get_connect_account(request.user)
    purchases = Purchase.objects.filter(Q(session__competition__admin=request.user) & (Q(type=Purchase.SPECTATOR) | Q(type=Purchase.SPECTATOR_VIA_CODE))).order_by('-session__competition__date','-session__time')
    totals = purchases.values('session_id','session__finished','session__competition__date','session__name','session__competition__name','session__spectator_fee').annotate(total=Sum('amount')-Sum('our_fee'),spectators=Count('id'))

    context = {
        'title':'Earnings',
        'connect_status':connect_status,
        'account':account,
        'totals': totals,
    }
    return render(request,'account/earnings.html',context)

@login_required(login_url='/account/login/admin/')
def spectator_list_csv(request,session_id):
    session = Session.objects.get(pk=session_id)
    spectators = Purchase.objects.filter(Q(session=session) & (Q(type=Purchase.SPECTATOR) | Q(type=Purchase.SPECTATOR_VIA_CODE)))
    
    headers = ['First Name','Last Name', 'Email', 'Type']  
   
    output = []
    response = HttpResponse (content_type='text/csv')
    writer = csv.writer(response)
    #Header
    writer.writerow(headers)
    for s in spectators:
        out = [s.user.first_name,s.user.last_name,s.user.email]
        if s.type == Purchase.SPECTATOR:
            out.append('Purchase')
        else:
            out.appsend('Access Code')
        output.append(out)
    #CSV Data
    writer.writerows(output)
    return response

@login_required(login_url='/account/login/admin/')
def stripe_payment_screen(request,session_id,type,qty):
    session = Session.objects.get(pk=session_id)
    if type == Purchase.ACCESS_CODE:
        message = "You are purchasing " + str(qty) + " additonal access code uses for $" + str(settings.ACCESS_CODE_COST) + ".00 each."
        cost = settings.ACCESS_CODE_COST
        success_message = "Additional Access Code uses purchased"
        redirect=''
    elif type == Purchase.SPECTATOR:
        if session.finished:
            type = Purchase.SCOREBOARD
            message = "You are purchasing access to scoreboard and videos for " + session.full_name() + " for $" + str(settings.SCOREBOARD_COST) + ".00"
            cost = settings.SCOREBOARD_COST
            success_message = "Access to " + session.full_name() + " purchased, you may now view the scoreboard and videos."
            redirect="/scoreboard/?ses=" + str(session_id)
        else: #session not done so normal spectator
            message = "You are purchasing access to " + session.full_name() + " for $" + str(session.spectator_fee)
            cost = session.spectator_fee
            success_message = "Access to " + session.full_name() + " purchased, you may now view the competition."
            redirect="/spectate/" + str(session_id) + "/single/"

    total = cost * qty
    intent_secret = stripe_handler.create_intent(request.user,session,type,cost,qty)
    methods = stripe_handler.get_customer_cards(request.user)
    if settings.STRIPE_TEST_MODE:
        pk = settings.STRIPE_PUBLIC_KEY_TEST
    else:
        pk = settings.STRIPE_PUBLIC_KEY
    context = {
        'session': session,
        'intent_secret':intent_secret,
        'stripe_pk':pk,
        'total':total,
        'success_message':success_message,
        'message':message,
        'methods':methods,
        'redirect':redirect,
    }
    return render(request,'account/stripe_payment_screen.html',context)

@login_required(login_url='/account/login/admin/')
def stripe_connect_account(request,session_id):
    user = request.user
    if user.stripe_connect_account == '':
        user.stripe_connect_account = stripe_handler.create_connect_account()
        user.save()
    #send them off to stripe
    url = stripe_handler.get_account_link(user,session_id)
    return redirect(url)

@login_required(login_url='/account/login/admin/')
def stripe_goto_dashboard(request):
    user = request.user
    url = stripe_handler.get_dashboard_link(user)
    return redirect(url)


@csrf_exempt
def stripe_webhook(request):
    if settings.STRIPE_TEST_MODE:
        stripe.api_key = settings.STRIPE_API_KEY_TEST
        endpoint_secret = settings.STRIPE_WEBHOOK_SECRET_TEST
    else:
        stripe.api_key = settings.STRIPE_API_KEY
        endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
    
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
        payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the checkout.session.completed event
    if event['type'] == 'charge.succeeded':
        #charge payment for session activation
        response = event['data']['object']
        session = Session.objects.get(pk=response["metadata"]["session_id"])
        if response["metadata"]["type"] == Purchase.PANEL:
            session.paid=True
            session.save()
        elif response["metadata"]["type"] == Purchase.ACCESS_CODE:
            session.access_code_total = session.access_code_total + int(response["metadata"]["quantity"])
            session.save()
        elif response["metadata"]["type"] == Purchase.SPECTATOR:
            user = User.objects.get(pk=response["metadata"]["user"])
            user.sessions_available.add(session)
        elif response["metadata"]["type"] == Purchase.SCOREBOARD:
            user = User.objects.get(pk=response["metadata"]["user"])
            user.sessions_available.add(session)

        purchase = Purchase(user_id=response["metadata"]["user"],session=session,type=response["metadata"]["type"],
                            amount=response["metadata"]["individual_amount"],quantity=response["metadata"]["quantity"],
                            our_fee=response["metadata"]["our_fee"],stripe_payment=response['id'])
        purchase.save()

        #create the purchase

        #now update customers default payment method to wahtever was just used
        try:
            stripe.Customer.modify(response["customer"],invoice_settings={'default_payment_method':response["payment_method"]})
        except:
            chargefail = True

    return HttpResponse(status=200)