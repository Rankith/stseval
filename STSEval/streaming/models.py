from django.db import models
import datetime
import app
from management.models import Session

# Create your models here.
class WowzaStream(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE,default=None,null=True)
    disc = models.CharField(max_length=10,default='MAG')
    event = models.CharField(max_length=10,default='FX')
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