"""
Definition of models.
"""

from django.db import models
from management.models import Competition, Athlete, Judge, Session, Event

# Create your models here.
class Twitch(models.Model):
    code = models.CharField(max_length=255)
    access_token = models.CharField(max_length=255,blank=True)
    refresh_token = models.CharField(max_length=255,blank=True)
    expiration = models.DateTimeField()
    user_id = models.CharField(max_length=50,blank=True)
    user_stream = models.CharField(max_length=255,blank=True)

class StreamMarkers(models.Model):
    position_seconds_start = models.IntegerField(default=0)
    position_seconds_end = models.IntegerField(default=0)
    
class Routine(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE,default=None,null=True)
    disc = models.CharField(max_length=10)
    event = models.ForeignKey(Event, on_delete=models.SET_NULL,blank=True,null=True)
    athlete = models.ForeignKey(Athlete, on_delete=models.SET_NULL,null=True)
    NEW = 'N'
    STARTED = 'S'
    ATHLETE_DONE = 'AD'
    REVIEW_DONE = 'RD'
    FINISHED = 'F'
    DELETED = 'D'
    MANUAL = 'M'
    ROUTINE_STATUS = [
        (NEW,'New'),
        (STARTED,'Started'),
        (ATHLETE_DONE,'Athlete Done'),
        (REVIEW_DONE,'Review Done'),
        (FINISHED,'Finished'),
        (DELETED,'Deleted'),
        (MANUAL,'Manual'),
        ]
    status = models.CharField(max_length=2,choices=ROUTINE_STATUS,default=NEW)
    e1_done = models.BooleanField(default=False)
    e2_done = models.BooleanField(default=False)
    e3_done = models.BooleanField(default=False)
    e4_done = models.BooleanField(default=False)
    e1_include = models.BooleanField(default=True)
    e2_include = models.BooleanField(default=True)
    e3_include = models.BooleanField(default=True)
    e4_include = models.BooleanField(default=True)
    e1_name = models.CharField(max_length=50,blank=True)
    e2_name = models.CharField(max_length=50,blank=True)
    e3_name = models.CharField(max_length=50,blank=True)
    e4_name = models.CharField(max_length=50,blank=True)
    d1_name = models.CharField(max_length=50,blank=True)
    #start_time = models.DateTimeField(null=True,blank=True)
    #athlete_done_time = models.DateTimeField(null=True,blank=True)
    #d1_done_time = models.DateTimeField(null=True,blank=True)
    score_elements = models.IntegerField(default=0)
    score_difficulty = models.FloatField(default=0)
    score_groups = models.FloatField(default=0)
    score_bonus = models.FloatField(default=0)
    score_connection = models.FloatField(default=0)
    score_neutral = models.FloatField(default=0)
    score_e1 = models.FloatField(default=0)
    score_e2 = models.FloatField(default=0)
    score_e3 = models.FloatField(default=0)
    score_e4 = models.FloatField(default=0)
    score_e = models.FloatField(default=0)
    score_d = models.FloatField(default=0)
    score_final = models.FloatField(default=0)
    start_time = models.BigIntegerField(blank=True,null=True)
    athlete_done_time = models.BigIntegerField(blank=True,null=True)
    d1_done_time = models.BigIntegerField(blank=True,null=True)
    video_saved = models.BooleanField(default=False)
    video_converted = models.BooleanField(default=False)
    d_judge = models.CharField(max_length=2,default='D1')
    video_file= models.FileField(null=True)
    video_from_backup = models.BooleanField(default=False)
    #stream = models.CharField(max_length=255)
    def routine_length(self):
        return self.athlete_done_time - self.start_time


class EJuryDeduction(models.Model):
    routine = models.ForeignKey(Routine, on_delete=models.CASCADE)
    judge = models.IntegerField()
    deduction = models.IntegerField()
    editor = models.CharField(max_length=2,default='E')
    time_stamp = models.BigIntegerField(blank=True,null=True)
    time_stamp_relative = models.IntegerField(default=0)
    artistry_type = models.CharField(max_length=10,blank=True,default='')
    ADD = 'Add'
    EDIT = 'Edit'
    DELETE = 'Delete'
    ACTION_TYPE = [
        (ADD,'Add'),
        (EDIT,'Edit'),
        (DELETE,'Delete'),
        ]
    action = models.CharField(max_length=6,choices=ACTION_TYPE,default=ADD)

def backup_video_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'routine_videos/{0}/{1}/bv_{2}_{3}'.format(instance.session.id, instance.event.name, instance.athlete.name.replace(" ",""),filename)

class BackupVideo(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE,default=None,null=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    athlete = models.ForeignKey(Athlete, on_delete=models.SET_NULL,null=True)
    video_file= models.FileField(upload_to=backup_video_path, null=True)
    reviewed = models.BooleanField(default=False)
    converted = models.BooleanField(default=False)