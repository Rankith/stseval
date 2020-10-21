from django.shortcuts import render,redirect
from django.http import HttpRequest,JsonResponse,HttpResponse
from django.template import RequestContext
from datetime import datetime
from .forms import CompetitionForm
from .models import Competition,Session,Athlete

# Create your views here.
def setup_competition(request):
    context = {
        'title': 'Compeition Setup (1/7)',
    }
    return render(request,'management/setup_competition.html',context)

def competition_list(request):
    comps = Competition.objects.filter(disc=request.GET.get('disc'))

    context = {
        'comps':comps,
    }
    return render(request, 'management/competition_list.html', context)

def competition_form(request):
    if request.method == 'POST':
        id = request.POST.get('id','-1')
        if id != '-1':
            form = CompetitionForm(request.POST,instance=Competition.objects.get(pk=id))
        else:
            form = CompetitionForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponse(status=200)
        else:
            return HttpResponse(status=404)
    else:
        id = request.GET.get('id',-1)
        if id != -1:
            form = CompetitionForm(instance=Competition.objects.get(pk=id))
        else:
            form = CompetitionForm()
        return render(request, 'management/competition_form.html', {'form': form,'id':id})

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

def competition_delete(request):
    Competition.objects.filter(id=request.GET.get('id')).delete()
    return HttpResponse(status=200)

def session_list(request):
    sessions = Session.objects.filter(competition_id=request.GET.get('comp'))

    context = {
        'sessions':sessions,
    }
    return render(request, 'management/session_list.html', context)

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

def session_delete(request):
    Session.objects.filter(id=request.GET.get('id')).delete()
    return HttpResponse(status=200)

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

def athlete_list(request):
    athletes = Athlete.objects.filter(competition_id=request.GET.get('comp'),disc=request.GET.get('disc'))
    context = {
        'athletes':athletes,
    }
    return render(request, 'management/athlete_list.html', context)

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

def athlete_delete(request):
    Athlete.objects.filter(id=request.GET.get('id')).delete()
    return HttpResponse(status=200)
