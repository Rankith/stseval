from django.shortcuts import render
from datetime import datetime,timezone
from django.http import HttpRequest,JsonResponse,HttpResponse
from streaming.wowza import LiveStreams, WOWZA_API_KEY, WOWZA_ACCESS_KEY
from streaming.models import WowzaStream
import app.firebase
from management.models import Camera

# Create your views here.
def camera(request):
    camera = Camera.objects.get(pk=request.session.get('camera'))
    #make stream target
    if camera.stream == None:
        create_stream(camera)
    context = {
        'stream':camera.stream,
        'disc':camera.session.competition.disc,
        'comp':camera.session.competition,
        }

    return render(request,'streaming/camera.html',context)

def create_stream(camera):
    response = wowza_instance = LiveStreams(
        api_key = WOWZA_API_KEY,
        access_key = WOWZA_ACCESS_KEY
    )
    new_name = str(camera.session.id) + "-camera" + str(camera.id)
    #stream_id = response['live_stream']['id']
    # Create a Live Stream
    response = wowza_instance.create({
        'name': new_name,
        'broadcast_location': 'us_west_oregon',
        'encoder': 'other_webrtc',
        'aspect_ratio_width': 1280,
        'aspect_ratio_height': 720,
        'transcoder_type':'transcoded',
        'hosted_page':False,
        'player_responsive':True,
        'low_latency':True
    })

    stream = WowzaStream(stream_id=response['live_stream']['id'],name=new_name,sdp_url=response['live_stream']['source_connection_information']['sdp_url'],application_name=response['live_stream']['source_connection_information']['application_name'],stream_name=response['live_stream']['source_connection_information']['stream_name'],hls_playback_url=response['live_stream']['player_hls_playback_url'])
    stream.save()
    camera.stream = stream
    camera.save()
    return True

def create_camera_stream(request):
    camera = Camera.objects.get(pk=request.session.get('camera'))
    #make stream target
    if camera.stream == None:
        create_stream(camera)

    return JsonResponse({"test":"test"},safe=False)

def get_stream_connection_info(request):
    stream = Camera.objects.get(pk=request.session.get('camera')).stream
    #app.firebase.routine_set_stream(request.POST.get('comp') + request.POST.get('disc') + request.POST.get('event'),stream.id)
   
    return JsonResponse({
        "stream":stream.id,
    },safe=False)

def start_stream(request):
    stream = Camera.objects.get(pk=request.session.get('camera')).stream
    
    wowza_instance = LiveStreams(
        api_key = WOWZA_API_KEY,
        access_key = WOWZA_ACCESS_KEY
    )
    response = wowza_instance.start(stream.stream_id)
    try:
        stream.status = response['live_stream']['state']
    except:
        stream.status = WowzaStream.STOPPED
    stream.last_connected = datetime.now(timezone.utc)
    stream.save()
    app.firebase.set_stream(stream)
    return JsonResponse(response,safe=False)

def stop_stream(request):
    stream = Camera.objects.get(pk=request.session.get('camera')).stream
    wowza_instance = LiveStreams(
        api_key = WOWZA_API_KEY,
        access_key = WOWZA_ACCESS_KEY
    )
    response = wowza_instance.stop(stream.stream_id)

    try:
        stream.status = response['live_stream']['state']
    except:
        stream.status = WowzaStream.STARTED
    stream.save()
    app.firebase.set_stream(stream)

    return JsonResponse(response,safe=False)

def get_state(request):
    stream = Camera.objects.get(pk=request.session.get('camera')).stream
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
    stream = Camera.objects.get(pk=request.session.get('camera')).stream
    status = request.POST.get('status')

    if status=="connected":
        stream.connected = True
        stream.last_connected = datetime.now(timezone.utc)
        stream.status = WowzaStream.STARTED
    else:
         stream.connected = False
    stream.save()
    app.firebase.set_stream(stream)

    return HttpResponse(status=200)


def get_stats(request):
    stream = Camera.objects.get(pk=request.session.get('camera')).stream
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
            if connected:
                stream.last_connected = datetime.now(timezone.utc)
            stream.save()
            app.firebase.set_stream_connected(stream.id,stream.connected)
    except:
        stream.connected = False
        stream.save()


    return JsonResponse(response,safe=False)
