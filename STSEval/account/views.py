from django.shortcuts import render,redirect
from .models import User
from .forms import SignUpForm,LoginForm
from django.contrib.auth import authenticate, login

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

def loginview(request):
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

