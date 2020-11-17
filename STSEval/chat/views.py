from django.shortcuts import render
import app.views
from django.http import HttpRequest,JsonResponse,HttpResponse
from management.models import Camera,Judge,Session,Team


# Create your views here.
def send_message(request):
    to = request.POST.get('to')
    message = request.POST.get('message')
    app.firebase.chat_send_message(request.session.get('session'),request.session.get('chat_name'),to,message)

    return HttpResponse(status=200)

def get_eligable_chats(request):
    type = request.session.get('type')
    event = request.session.get('event','')
    session_id = request.session.get('session')
    chats = []
    
    if type[0:1] == 'e':
        judges = Judge.objects.filter(session_id=session_id,event__name=event).first()
        chats.append(event + " D1 - " + judges.d1)
        chats.append(event + " Panel")
        chats.append("Meet Administrator")
    elif type[0:1] == 'd':
        judges = Judge.objects.filter(session_id=session_id,event__name=event).first()
        if judges.e1 != "" and judges.e1 != " ":
            chats.append(event + " E1 - " + judges.e1)
        if judges.e2 != "" and judges.e2 != " ":
            chats.append(event + " E2 - " + judges.e2)
        if judges.e3 != "" and judges.e3 != " ":
            chats.append(event + " E3 - " + judges.e3)
        if judges.e4 != "" and judges.e4 != " ":
            chats.append(event + " E4 - " + judges.e4)
        chats.append(event + " Panel")
        #teams = Team.objects.filter(session_id=session_id)
        #for team in teams:
            #chats.append('Coach - ' + team.abbreviation)
        chats.append("Meet Administrator")
    elif type == 'coach':
        judges = Judge.objects.filter(session_id=session_id).order_by('event__display_order')
        #for judge in judges:
            #if judge.d1 != "" and judge.d1 != " ":
                #chats.append(judge.event.name + " D1 - " + judge.d1)
        chats.append("Meet Administrator")
    elif type == 'admin':
        judges = Judge.objects.filter(session_id=session_id).order_by('event__display_order')
        for judge in judges:
            if judge.d1 != "" and judge.d1 != " ":
                chats.append(judge.event.name + " D1 - " + judge.d1)
            if judge.e1 != "" and judge.e1 != " ":
                chats.append(judge.event.name + " E1 - " + judge.e1)
            if judge.e2 != "" and judge.e2 != " ":
                chats.append(judge.event.name + " E2 - " + judge.e2)
            if judge.e3 != "" and judge.e3 != " ":
                chats.append(judge.event.name + " E3 - " + judge.e3)
            if judge.e4 != "" and judge.e4 != " ":
                chats.append(judge.event.name + " E4 - " + judge.e4)
            chats.append(judge.event.name + " Panel")
        teams = Team.objects.filter(session_id=session_id)
        for team in teams:
            chats.append('Coach - ' + team.abbreviation)

    return JsonResponse(chats,safe=False)
