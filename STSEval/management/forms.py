"""
Definition of forms.
"""

from django import forms
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.forms import ModelForm,CheckboxSelectMultiple,ImageField
from django.utils.safestring import mark_safe
from management.models import Competition,Session,Athlete,Judge,Team,Camera,Event,Sponsor

class DateInput(forms.DateInput):
    input_type = 'date'

class TimeInput(forms.TimeInput):
    input_type = 'time'

class CompetitionForm(ModelForm):
    class Meta:
        model = Competition
        fields = ['disc','name','type','date']
        widgets = {'disc': forms.HiddenInput(),
                   'name':forms.TextInput(attrs={'class':'management-input'}),
                   'date':DateInput(attrs={'class':'management-input'}),
                   'type':forms.Select(attrs={'class':'selectpicker','data-style':'btn-main'})}

    def __init__(self, *args, **kwargs):
        self._user = kwargs.pop('user')
        super(CompetitionForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        inst = super(CompetitionForm, self).save(commit=False)
        inst.admin = self._user
        if commit:
            inst.save()
            self.save_m2m()
        return inst

class SessionForm(ModelForm):
    class Meta:
        model = Session
        fields = ['competition','name','time','spectator_fee']
        widgets = {'competition': forms.HiddenInput(),
                   'name':forms.TextInput(attrs={'class':'management-input'}),
                   'spectator_fee':forms.TextInput(attrs={'class':'management-input','placeholder':'2.00 min.'}),
                   'time':TimeInput(attrs={'class':'management-input'})}

    def clean(self):
        data = self.cleaned_data
        if data.get('spectator_fee') < 2:
            raise forms.ValidationError('Spectator Fee has a $2.00 minimum')
        else:
            return data

class JudgeForm(ModelForm):
    class Meta:
        model = Judge
        fields = ['session','event','d1','d1_affil','d1_email','d1_password',
                  'd2','d2_affil','d2_email','d2_password',
                  'e1','e1_affil','e1_email','e1_password',
                  'e2','e2_affil','e2_email','e2_password',
                  'e3','e3_affil','e3_email','e3_password',
                  'e4','e4_affil','e4_email','e4_password']
        widgets = {'session': forms.HiddenInput(),
                   'event': forms.HiddenInput(),
                   'd1':forms.TextInput(attrs={'placeholder':'Judge Full Name'}),'d1_affil':forms.TextInput(attrs={'placeholder':'Country'}),'d1_email':forms.EmailInput(attrs={'placeholder':'example@email.com'}),'d1_password':forms.TextInput(attrs={'placeholder':'password'}),
                   'd2':forms.TextInput(attrs={'placeholder':'Judge Full Name'}),'d2_affil':forms.TextInput(attrs={'placeholder':'Country'}),'d2_email':forms.EmailInput(attrs={'placeholder':'example@email.com'}),'d2_password':forms.TextInput(attrs={'placeholder':'password'}),
                   'e1':forms.TextInput(attrs={'placeholder':'Judge Full Name'}),'e1_affil':forms.TextInput(attrs={'placeholder':'Country'}),'e1_email':forms.EmailInput(attrs={'placeholder':'example@email.com'}),'e1_password':forms.TextInput(attrs={'placeholder':'password'}),
                   'e2':forms.TextInput(attrs={'placeholder':'Judge Full Name'}),'e2_affil':forms.TextInput(attrs={'placeholder':'Country'}),'e2_email':forms.EmailInput(attrs={'placeholder':'example@email.com'}),'e2_password':forms.TextInput(attrs={'placeholder':'password'}),
                   'e3':forms.TextInput(attrs={'placeholder':'Judge Full Name'}),'e3_affil':forms.TextInput(attrs={'placeholder':'Country'}),'e3_email':forms.EmailInput(attrs={'placeholder':'example@email.com'}),'e3_password':forms.TextInput(attrs={'placeholder':'password'}),
                   'e4':forms.TextInput(attrs={'placeholder':'Judge Full Name'}),'e4_affil':forms.TextInput(attrs={'placeholder':'Country'}),'e4_email':forms.EmailInput(attrs={'placeholder':'example@email.com'}),'e4_password':forms.TextInput(attrs={'placeholder':'password'})
                   };
    def __init__(self, *args, **kwargs):
        super(JudgeForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'judge-input'
            visible.field.widget.attrs['onchange'] = 'FlagChange(this)'

    def clean(self):
        data = self.cleaned_data
        if (data.get('d1_email', "") != "" and data.get('d1_password', "") == "") or (data.get('d2_email', "") != "" and data.get('d2_password', "") == "") or (data.get('e1_email', "") != "" and data.get('e1_password', "") == "") or (data.get('e2_email', "") != "" and data.get('e2_password', "") == "") or (data.get('e3_email', "") != "" and data.get('e3_password', "") == "") or (data.get('e4_email', "") != "" and data.get('e4_password', "") == ""):
            raise forms.ValidationError('All entered judges must have a password')
        else:
            return data

class TeamForm(ModelForm):
    class Meta:
        model = Team
        fields = ['session','name','abbreviation','head_coach_email','coach_password']
        widgets = {'session': forms.HiddenInput(),
                   'name':forms.TextInput(attrs={'class':'management-input'}),
                   'abbreviation':forms.TextInput(attrs={'class':'management-input'}),
                   'head_coach_email':forms.EmailInput(attrs={'placeholder':'example@email.com','class':'management-input','onchange':'EmailChange()'}),
                   'coach_password':forms.TextInput(attrs={'placeholder':'password','class':'management-input'})}

class AthleteForm(ModelForm):
    class Meta:
        model = Athlete
        fields = ['team','level','name','rotation']
        widgets = {'team': forms.HiddenInput(),
                   'name':forms.TextInput(attrs={'class':'management-input'}),
                   'rotation':forms.TextInput(attrs={'class':'management-input'}),
                   'level':forms.Select(attrs={'class':'selectpicker management-input','data-style':'btn-main'})}

class CameraForm(ModelForm):
    class Meta:
        model = Camera
        fields = ['session','name','email','password','location','teams','events']
        widgets = {'session': forms.HiddenInput(),
                   'name':forms.TextInput(attrs={'class':'management-input'}),
                   'email':forms.EmailInput(attrs={'placeholder':'example@email.com','class':'management-input','onchange':'EmailChange()'}),
                   'password':forms.TextInput(attrs={'placeholder':'password','class':'management-input'}),
                   'location':forms.TextInput(attrs={'class':'management-input'})}

    def __init__(self, *args, **kwargs):
        session = kwargs.pop('session')
        session = Session.objects.get(pk=session)
        super(CameraForm, self).__init__(*args, **kwargs)
        self.fields["events"].widget = CheckboxSelectMultiple()
        self.fields["events"].widget.attrs['class'] = 'camera-checkbox'
        self.fields["events"].queryset = Event.objects.filter(disc=session.competition.disc)
        self.fields['events'].label_from_instance = lambda obj: "%s - %s" % (obj.name, obj.full_name)
        self.fields["teams"].widget = CheckboxSelectMultiple()
        self.fields["teams"].widget.attrs['class'] = 'camera-checkbox'
        self.fields["teams"].queryset = Team.objects.filter(session=session)

class ImagePreviewWidget(forms.widgets.FileInput):
    def render(self, name, value, attrs=None, **kwargs):
        input_html = super().render(name, value, attrs=None, **kwargs)
        if value:
            img_html = mark_safe(f'<br><br><img src="{value.url}" height="288px"/>')
        else:
            img_html=""
        return f'{input_html}{img_html}'

class SponsorForm(ModelForm):
    class Meta:
        model = Sponsor
        fields = ['session','name','url','image']
        widgets = {'session': forms.HiddenInput(),
                   'name':forms.TextInput(attrs={'class':'management-input'}),
                   'url':forms.TextInput(attrs={'class':'management-input','placeholder':'full url'}),
                   'image':ImagePreviewWidget()}
           