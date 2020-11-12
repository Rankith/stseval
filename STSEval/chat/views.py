from django.shortcuts import render
import app.views
from django.http import HttpRequest,JsonResponse,HttpResponse

# Create your views here.
def send_message(request):
    to = request.POST.get('to')
    message = request.POST.get('message')
    app.firebase.chat_send_message(request.session.get('session'),request.session.get('chat_name'),to,message)

    return HttpResponse(status=200)
