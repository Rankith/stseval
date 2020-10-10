from django.shortcuts import render
from django.http import HttpRequest,JsonResponse,HttpResponse
from streaming.wowza import LiveStreams, WOWZA_API_KEY, WOWZA_ACCESS_KEY
from streaming.models import WowzaStream
import app.firebase

# Create your views here.
def camera(request):
    comp = request.GET.get('c')
    disc = request.GET.get('d')
    event = request.GET.get('e')
    stream = WowzaStream.objects.filter(competition_id=comp,disc=disc,event=event).first()
    if stream == None:
        response = wowza_instance = LiveStreams(
            api_key = WOWZA_API_KEY,
            access_key = WOWZA_ACCESS_KEY
        )
        #stream_id = response['live_stream']['id']
        # Create a Live Stream
        response = wowza_instance.create({
            'name': comp + disc + event,
            'broadcast_location': 'us_west_oregon',
            'encoder': 'other_webrtc',
            'aspect_ratio_width': 1280,
            'aspect_ratio_height': 720,
            'transcoder_type':'transcoded',
            'hosted_page':False,
            'player_responsive':True,
            'low_latency':True
        })

        stream = WowzaStream(stream_id=response['live_stream']['id'],name='Test1',sdp_url=response['live_stream']['source_connection_information']['sdp_url'],application_name=response['live_stream']['source_connection_information']['application_name'],stream_name=response['live_stream']['source_connection_information']['stream_name'])
        stream.competition_id = comp
        stream.disc = disc
        stream.event = event
        stream.save()
    context = {
        'stream':stream,
        'disc':disc,
        'event':event,
        'comp':comp,
        }

    return render(request,'app/camera.html',context)

def create_camera_stream(request):
    response = wowza_instance = LiveStreams(
        api_key = WOWZA_API_KEY,
        access_key = WOWZA_ACCESS_KEY
    )
    #stream_id = response['live_stream']['id']
    # Create a Live Stream
    response = wowza_instance.create({
        'name': 'Test1',
        'broadcast_location': 'us_west_oregon',
        'encoder': 'other_webrtc',
        'aspect_ratio_width': 1280,
        'aspect_ratio_height': 720,
        'transcoder_type':'transcoded',
        'hosted_page':False,
        'player_responsive':True,
        'low_latency':True
    })

    stream = WowzaStream(stream_id=response['live_stream']['id'],name='Test1',sdp_url=response['live_stream']['source_connection_information']['sdp_url'],application_name=response['live_stream']['source_connection_information']['application_name'],stream_name=response['live_stream']['source_connection_information']['stream_name'])
    stream.competition_id = request.POST.get('comp')
    stream.disc = request.POST.get('disc')
    stream.event = request.POST.get('event')
    stream.save()

    return JsonResponse({"test":"test"},safe=False)

def get_stream_connection_info(request):
    stream = WowzaStream.objects.filter(competition_id=request.POST.get('comp'),disc=request.POST.get('disc'),event=request.POST.get('event')).first()
    app.firebase.routine_set_stream(request.POST.get('comp') + request.POST.get('disc') + request.POST.get('event'),stream.id)
    #app.firebase.set_stream(request.POST.get('comp') + request.POST.get('disc') + request.POST.get('event'),stream)
    return JsonResponse({
        "stream":stream.id,
    },safe=False)

def start_stream(request):
    stream = WowzaStream.objects.filter(competition_id=request.POST.get('comp'),disc=request.POST.get('disc'),event=request.POST.get('event')).first()
    
    wowza_instance = LiveStreams(
        api_key = WOWZA_API_KEY,
        access_key = WOWZA_ACCESS_KEY
    )
    response = wowza_instance.start(stream.stream_id)
    try:
        stream.status = response['live_stream']['state']
    except:
        stream.status = WowzaStream.STOPPED
    stream.save()
    app.firebase.set_stream(stream)
    return JsonResponse(response,safe=False)

def stop_stream(request):
    stream = WowzaStream.objects.filter(competition_id=request.POST.get('comp'),disc=request.POST.get('disc'),event=request.POST.get('event')).first()
    wowza_instance = LiveStreams(
        api_key = WOWZA_API_KEY,
        access_key = WOWZA_ACCESS_KEY
    )
    response = wowza_instance.stop(stream.stream_id)

    return JsonResponse(response,safe=False)

def get_state(request):
    stream = WowzaStream.objects.filter(competition_id=request.POST.get('comp'),disc=request.POST.get('disc'),event=request.POST.get('event')).first()
    wowza_instance = LiveStreams(
        api_key = WOWZA_API_KEY,
        access_key = WOWZA_ACCESS_KEY
    )
    response = wowza_instance.info(stream.stream_id,'state')
    try:
        if stream.status != response['live_stream']['state']:
            stream.status = response['live_stream']['state']
            stream.save()
            app.firebase.set_stream_status(stream.id,stream.status)
    except:
        stream.status = WowzaStream.STOPPED
        stream.save()

    return JsonResponse(response,safe=False)

def update_stream_status(request):
    stream = WowzaStream.objects.filter(competition_id=request.POST.get('comp'),disc=request.POST.get('disc'),event=request.POST.get('event')).first()
    status = request.POST.get('status')

    if status=="connected":
        stream.connected = True
        stream.status = WowzaStream.STARTED
    else:
         stream.connected = False
    stream.save()
    app.firebase.set_stream(stream)

    return HttpResponse(status=200)


def get_stats(request):
    stream = WowzaStream.objects.filter(competition_id=request.POST.get('comp'),disc=request.POST.get('disc'),event=request.POST.get('event')).first()
    wowza_instance = LiveStreams(
        api_key = WOWZA_API_KEY,
        access_key = WOWZA_ACCESS_KEY
    )
    response = wowza_instance.info(stream.stream_id,'stats')
    try:
        if response['live_stream']['connected']['value'] == 'Yes':
            connected = True
        else:
            connected = False
        if stream.connected != connected:
            stream.connected = connected
            stream.save()
            app.firebase.set_stream_connected(stream.id,stream.connected)
    except:
        stream.connected = False
        stream.save()


    return JsonResponse(response,safe=False)
