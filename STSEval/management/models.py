from django.db import models

# Create your models here.
class Competition(models.Model):
    name = models.CharField(max_length=75)
    disc = models.CharField(max_length=10)
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
    def full_name(self):
       return self.competition.name + " - " + self.competition.get_type_display() + " - " + self.name

class Team(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    abbreviation = models.CharField(max_length=4,blank=True)
    def __str__(self):
        return self.name

class AthleteLevel(models.Model):
    disc = models.CharField(max_length=10)
    name = models.CharField(max_length=25)
    abbreviation = models.CharField(max_length=6, blank=True)
    def __str__(self):
        return self.name

class Athlete(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE,default=None,null=True)
    name = models.CharField(max_length=50)
    level = models.ForeignKey(AthleteLevel,on_delete=models.CASCADE,default=None,null=True)
    age = models.IntegerField(default=8)
    rotation =  models.CharField(max_length=2,default='A')
    def __str__(self):
        return self.team.name + " - " + self.level + " - " + self.name

class Judge(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    event = models.CharField(max_length=10)
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