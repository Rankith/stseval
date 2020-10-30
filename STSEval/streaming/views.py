from django.shortcuts import render
from datetime import datetime,timezone
from django.http import HttpRequest,JsonResponse,HttpResponse
from streaming.wowza import LiveStreams, Transcoders, StreamTargets, WOWZA_API_KEY, WOWZA_ACCESS_KEY
from streaming.models import WowzaStream
import app.firebase
from management.models import Camera

# Create your views here.
def camera(request):
    camera = Camera.objects.get(pk=request.session.get('camera'))
    #make stream target
    if camera.stream == None:
        create_stream(camera)
    #create_stream_passthrough(camera)
    context = {
        'stream':camera.stream,
        'disc':camera.session.competition.disc,
        'comp':camera.session.competition,
        'scoreboard':True,
        }

    return render(request,'streaming/camera.html',context)

def create_stream_passthrough(camera):
    #create fastly stream target
    response = wowza_instance =  StreamTargets(
        api_key = WOWZA_API_KEY,
        access_key = WOWZA_ACCESS_KEY
    )
    new_name = str(camera.session.id) + "-camera" + str(camera.id) + " / Fastly Target"
    response = wowza_instance.create_fastly({
        'name': new_name,
    })
    fastly_target = response['stream_target_fastly']['id']

    #create passthrough transcoder
    response = wowza_instance =  Transcoders(
        api_key = WOWZA_API_KEY,
        access_key = WOWZA_ACCESS_KEY
    )
    new_name = str(camera.session.id) + "-camera" + str(camera.id) + " / Transcoder"
    response = wowza_instance.create({
        'name': new_name,
        'billing_mode': 'pay_as_you_go',
        'broadcast_location': 'us_west_oregon',
        'delivery_method': 'push',
        'protocol': "webrtc",
        'transcoder_type':'passthrough',
        'low_latency':True
    })

    transcoder_id = response['transcoder']['id']
    application_name = response['transcoder']['application_name']
    stream_name = response['transcoder']['direct_playback_urls']['webrtc'][0]['stream_name']
    sdp_url = response['transcoder']['direct_playback_urls']['webrtc'][0]['url']

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
    app.firebase.set_stream(str(request.session.get('session')),stream)
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
    app.firebase.set_stream(str(request.session.get('session')),stream)

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
            app.firebase.set_stream_status(str(request.session.get('session')),stream.id,stream.status)
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
    app.firebase.set_stream(str(request.session.get('session')),stream)

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
            app.firebase.set_stream_connected(str(request.session.get('session')),stream.id,stream.connected)
    except:
        stream.connected = False
        stream.save()


    return JsonResponse(response,safe=False)
