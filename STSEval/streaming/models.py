from django.db import models
import datetime
import app

# Create your models here.
class WowzaStream(models.Model):
    stream_id = models.CharField(max_length=50)
    name = models.CharField(max_length=255)
    sdp_url = models.CharField(max_length=255)
    application_name = models.CharField(max_length=20)
    stream_name = models.CharField(max_length=20)
    STARTED = 'started'
    STARTING = 'starting'
    STOPPED = 'stopped'
    LIVE = 'live'
    STATUS = [
        (STARTED,'started'),
        (STARTING,'starting'),
        (STOPPED,'stopped'),
        (LIVE,'live'),
        ]
    status = models.CharField(max_length=10,choices=STATUS,default=STOPPED)
    connected = models.BooleanField(default=False)
    last_connected = models.DateTimeField(default=datetime.datetime.now)
    hls_playback_url = models.CharField(max_length=255,blank=True,default='')
    wowza_player_code = models.CharField(max_length=255,blank=True,default='')