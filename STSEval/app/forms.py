"""
Definition of forms.
"""

from django import forms
from django.db import models
from app.models import Routine
from django.forms import ModelForm,CheckboxSelectMultiple,ImageField
from management.models import Competition,Session,Athlete,Judge,Team,Camera,Event,Sponsor

class VideoUploadForm(ModelForm):
    class Meta:
        model = Routine
        
        fields = ['session','athlete','event','video_file']
        widgets = {'session': forms.HiddenInput(),
                   'video_file':forms.FileInput(attrs={'class':'management-input','accept': 'video/*'})}

    def __init__(self, *args, **kwargs):
        session = kwargs.pop('session')
        session = Session.objects.get(pk=session)
        team = kwargs.pop('team','')
        
        super(VideoUploadForm, self).__init__(*args, **kwargs)

        events = Event.objects.filter(disc=session.competition.disc) 
        self.fields["event"].widget = forms.Select(choices=[(event.name, event.full_name) for event in events])
        self.fields["event"].widget.attrs['class'] = 'selectpicker management-input'
        self.fields["event"].widget.attrs['data-style'] = 'btn-main'
        #self.fields['event'].label_from_instance = lambda obj: "%s - %s" % (obj.name, obj.full_name)

        self.fields["athlete"].widget = forms.Select()
        if team != '':
            team = Team.objects.filter(pk=team).first()
            self.fields["athlete"].queryset = Athlete.objects.filter(team=team)
        else:
            self.fields["athlete"].queryset = Athlete.objects.filter(team__session=session)
        self.fields["athlete"].widget.attrs['class'] = 'selectpicker management-input'
        self.fields["athlete"].widget.attrs['data-style'] = 'btn-main'
        self.fields['athlete'].label_from_instance = lambda obj: "%s - %s" % (obj.team.abbreviation, obj.name)


