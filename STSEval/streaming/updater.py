from datetime import datetime,timezone,timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from streaming.wowza import LiveStreams, WOWZA_API_KEY, WOWZA_ACCESS_KEY
from streaming.models import WowzaStream
from app.models import Routine,BackupVideo,ConversionSetting,Session
import app.firebase
from django.conf import settings
import os
import sys, socket
from django.db.models import Q

def start():
    try: #stupid hack for not multiple schedulers running
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(("127.0.0.1", 47200))
    except socket.error:
        print("!!!scheduler already started, DO NOTHING")
    else:
        scheduler = BackgroundScheduler()
        scheduler.add_job(check_and_stop_streams, 'interval', seconds=10)
        scheduler.add_job(check_convert_video, 'interval', seconds=20)
        scheduler.add_job(check_remove_old_videos, 'interval', hours=8)
        #check_remove_old_videos()
        #scheduler.add_job(check_update_wowza_player, 'interval', seconds=5)
        scheduler.start()
        print("scheduler started")


def check_remove_old_videos():
    routines = Routine.objects.filter(Q(session__competition__date__lt=datetime.now() - timedelta(days=30)) & Q(video_saved=True) & Q(status=Routine.FINISHED) & (Q(session__level=Session.WDP) | Q(session__level=Session.MDP))).exclude(video_file='')
    for r in routines:
        vidfile = r.video_file.path
        r.video_file.delete()
        if os.path.exists(vidfile):
            os.remove(vidfile)
        if os.path.exists(vidfile.replace("webm","mp4")):
            os.remove(vidfile.replace("webm","mp4"))

def convert_backup_video(bv):
    vidfile=bv.video_file.path
    conversionfile = os.path.splitext(vidfile)[0] + ".mp4"
    conversionfilename = os.path.splitext(bv.video_file.name)[0] + ".mp4"
    if os.path.exists(vidfile):
        os.system("ffmpeg -threads 2 -y -i {0} -c:v libx264 -profile:v main -vf format=yuv420p -c:a aac -movflags +faststart  {1}".format(vidfile,conversionfile))
        bv.video_file.name = conversionfilename
        bv.converted = True
        bv.save()
        os.remove(vidfile)
        app.firebase.set_backup_videos(bv.session.id,bv.event.name)
    else:
        bv.converted = True
        bv.save()

def check_convert_video():
        for bv in BackupVideo.objects.filter(converted=False):
            convert_backup_video(bv)
        routines = Routine.objects.filter(video_converted=False,video_saved=True,status=Routine.FINISHED)#.exclude(status=Routine.DELETED)
        for routine in routines:
            if ConversionSetting.objects.all().first().do_conversions:
                vidfile=routine.video_file.path
                if os.path.exists(vidfile):
                    os.system("ffmpeg -threads 2 -y -i {0} -c:v libx264 -profile:v main -vf format=yuv420p -c:a aac -movflags +faststart {1}".format(vidfile,vidfile.replace("webm","mp4")))
                    routine.video_converted = True
                    routine.save()
                    #os.remove(vidfile)

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
        #this sometimes marks a stream as not connected.  Maybe remove the connection status update if we can?
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