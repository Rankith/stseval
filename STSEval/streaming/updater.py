from datetime import datetime,timezone
from apscheduler.schedulers.background import BackgroundScheduler
from streaming.wowza import LiveStreams, WOWZA_API_KEY, WOWZA_ACCESS_KEY
from streaming.models import WowzaStream

def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(check_and_stop_streams, 'interval', seconds=20)
    scheduler.start()

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
                s.save()
        else:
            s.last_connected = datetime.now(timezone.utc)
            s.save()