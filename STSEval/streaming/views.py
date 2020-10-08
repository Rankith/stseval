from django.shortcuts import render
from django.http import HttpRequest,JsonResponse,HttpResponse
from streaming.wowza import LiveStreams, WOWZA_API_KEY, WOWZA_ACCESS_KEY
from streaming.models import WowzaStream

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

    return JsonResponse({
        "sdp_url":stream.sdp_url,
        "application_name":stream.application_name,
        "stream_name":stream.stream_name
    },safe=False)

def start_stream(request):
    stream = WowzaStream.objects.filter(competition_id=request.POST.get('comp'),disc=request.POST.get('disc'),event=request.POST.get('event')).first()
    wowza_instance = LiveStreams(
        api_key = WOWZA_API_KEY,
        access_key = WOWZA_ACCESS_KEY
    )
    response = wowza_instance.start(stream.stream_id)

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

    return JsonResponse(response,safe=False)

def get_stats(request):
    stream = WowzaStream.objects.filter(competition_id=request.POST.get('comp'),disc=request.POST.get('disc'),event=request.POST.get('event')).first()
    wowza_instance = LiveStreams(
        api_key = WOWZA_API_KEY,
        access_key = WOWZA_ACCESS_KEY
    )
    response = wowza_instance.info(stream.stream_id,'stats')

    return JsonResponse(response,safe=False)
