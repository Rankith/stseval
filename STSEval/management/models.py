from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from account.models import User
from streaming.models import WowzaStream

# Create your models here.
class Disc(models.Model):
    name = models.CharField(max_length=10)
    full_name = models.CharField(max_length=50)
    active = models.BooleanField(default=True)
    display_order = models.IntegerField(default=1)
    def __str__(self):
        return self.name
    class Meta:
        ordering = ["display_order"]

class Event(models.Model):
    disc = models.ForeignKey(Disc, on_delete=models.CASCADE,default=None,null=True)
    name = models.CharField(max_length=50)
    full_name = models.CharField(max_length=50)
    display_order = models.IntegerField(default=1)
    def __str__(self):
        return self.name
    class Meta:
        ordering = ["display_order"]

class Competition(models.Model):
    admin = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=75)
    disc = models.ForeignKey(Disc, on_delete=models.SET_NULL,default=None,null=True)
    TOURNAMENT = 'T'
    DUAL = 'D'
    INTRASQUAD = 'I'
    COMPETITION_TYPE = [
        (TOURNAMENT,'Tournament'),
        (DUAL,'Dual'),
        (INTRASQUAD,'Intrasquad'),
        ]
    type = models.CharField(max_length=2,choices=COMPETITION_TYPE,default=TOURNAMENT)
    date = models.DateField()
    def __str__(self):
       return self.name

class Session(models.Model):
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE,default=None,null=True)
    name = models.CharField(max_length=75)
    time = models.TimeField()
    spectator_fee = models.DecimalField(max_digits=6, decimal_places=2)
    test =  models.BooleanField(default=False)
    finished = models.BooleanField(default=False)
    active = models.BooleanField(default=False)
    def full_name(self):
       return self.competition.name + " - " + self.competition.get_type_display() + " - " + self.name

class Team(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    abbreviation = models.CharField(max_length=4,blank=True)
    head_coach_email = models.EmailField(max_length=100,blank=True)
    coach_password = models.CharField(max_length=50,blank=True)
    def __str__(self):
        return self.name

class AthleteLevel(models.Model):
    disc = models.ForeignKey(Disc, on_delete=models.CASCADE,default=None,null=True)
    name = models.CharField(max_length=25)
    abbreviation = models.CharField(max_length=14, blank=True)
    order = models.IntegerField(default=1)
    JO4567 = 'JO4567'
    JO8910 = 'JO8910'
    FIG = 'FIG'
    SCORING_TYPE = [
        (JO4567,'JO4567'),
        (JO8910,'JO8910'),
        (FIG,'FIG'),
        ]
    scoring_type = models.CharField(max_length=10,choices=SCORING_TYPE,default=FIG)
    def __str__(self):
        return self.name
    class Meta:
        ordering = ['order']

class Athlete(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE,default=None,null=True)
    name = models.CharField(max_length=50)
    level = models.ForeignKey(AthleteLevel,on_delete=models.SET_NULL,default=None,null=True)
    age = models.IntegerField(default=8)
    rotation =  models.CharField(max_length=2,default='A')
    order = models.IntegerField(default=1)
    events_competing = models.ManyToManyField(Event,related_name='events_competing_related',blank=True)
    events_count_for_team = models.ManyToManyField(Event,blank=True)
    def __str__(self):
        return self.team.name + " - " + self.level.name + " - " + self.name

class StartList(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    athlete = models.ForeignKey(Athlete, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    secondary_judging = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    order = models.IntegerField(default=1)

class Judge(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.SET_NULL,default=None,null=True)
    d1 = models.CharField(max_length=50,blank=True)
    d1_affil = models.CharField(max_length=50,blank=True)
    d1_email = models.EmailField(max_length=100,blank=True)
    d1_password = models.CharField(max_length=50,blank=True)
    d2 = models.CharField(max_length=50,blank=True)
    d2_affil = models.CharField(max_length=50,blank=True)
    d2_email = models.EmailField(max_length=100,blank=True)
    d2_password = models.CharField(max_length=50,blank=True)
    e1 = models.CharField(max_length=50,blank=True)
    e1_affil = models.CharField(max_length=50,blank=True)
    e1_email = models.EmailField(max_length=100,blank=True)
    e1_password = models.CharField(max_length=50,blank=True)
    e2 = models.CharField(max_length=50,blank=True)
    e2_affil = models.CharField(max_length=50,blank=True)
    e2_email = models.EmailField(max_length=100,blank=True)
    e2_password = models.CharField(max_length=50,blank=True)
    e3 = models.CharField(max_length=50,blank=True)
    e3_affil = models.CharField(max_length=50,blank=True)
    e3_email = models.EmailField(max_length=100,blank=True)
    e3_password = models.CharField(max_length=50,blank=True)
    e4 = models.CharField(max_length=50,blank=True)
    e4_affil = models.CharField(max_length=50,blank=True)
    e4_email = models.EmailField(max_length=100,blank=True)
    e4_password = models.CharField(max_length=50,blank=True)

class Camera(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    stream = models.ForeignKey(WowzaStream, on_delete=models.SET_NULL,null=True,default=None)
    name = models.CharField(max_length=50)
    email = models.EmailField(max_length=100)
    password = models.CharField(max_length=50)
    location = models.CharField(max_length=50)
    events = models.ManyToManyField(Event)
    teams = models.ManyToManyField(Team)
    def __str__(self):
        return self.location + "-" + self.name

def sponsor_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'sponsors/{0}/{1}'.format(instance.session.id, filename)

class Sponsor(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=sponsor_path)
    name = models.CharField(max_length=50)
    url = models.URLField(max_length=200,blank=True)

class RotationOrder(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    rotation =  models.CharField(max_length=2,default='A')
    order = models.IntegerField(default=1)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    class Meta:
        ordering = ['rotation','order']