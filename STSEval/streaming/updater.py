from datetime import datetime,timezone
from apscheduler.schedulers.background import BackgroundScheduler
from streaming.wowza import LiveStreams, WOWZA_API_KEY, WOWZA_ACCESS_KEY
from streaming.models import WowzaStream
import app.firebase

def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(check_and_stop_streams, 'interval', seconds=30)
    #scheduler.add_job(check_update_wowza_player, 'interval', seconds=5)
    scheduler.start()

def check_update_wowza_player():
    streams = WowzaStream.objects.filter(wowza_player_code='')
    wowza_instance = LiveStreams(
        api_key = WOWZA_API_KEY,
        access_key = WOWZA_ACCESS_KEY
    )
    for stream in streams:
        response = wowza_instance.info(stream.stream_id)
        stream.wowza_player_code = response['live_stream']['player_id']
        stream.save()
        app.firebase.set_stream(stream.camera_set.first().session.id,stream)

def check_and_stop_streams():
    AUTO_SHUTOFF = 900#15 minutes
    streams = WowzaStream.objects.filter(status=WowzaStream.STARTED)
    wowza_instance = LiveStreams(
        api_key = WOWZA_API_KEY,
        access_key = WOWZA_ACCESS_KEY
    )
    for s in streams:
        response = wowza_instance.info(s.stream_id,'stats')
        con = response["live_stream"]["connected"]["value"]
        if con == 'No':
            s.connected = False
            time_off = datetime.now(timezone.utc) - s.last_connected
            if time_off.seconds > AUTO_SHUTOFF:
                try:
                    response = wowza_instance.stop(s.stream_id)
                    try:
                        s.status = response['live_stream']['state']
                    except:
                        s.status = WowzaStream.STARTED
                except:
                    s.status = WowzaStream.STOPPED
            else:
                response = wowza_instance.info(s.stream_id,'state')
                try:
                    s.status = response['live_stream']['state']
                except:
                    s.status = WowzaStream.STARTED
            s.save()
        else:
            s.connected = True
            s.last_connected = datetime.now(timezone.utc)
            s.save()
        app.firebase.set_stream(s.camera_set.first().session.id,s)