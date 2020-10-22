"""
Definition of forms.
"""

from django import forms
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.forms import ModelForm
from management.models import Competition,Session,Athlete,Judge,Team

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

class SessionForm(ModelForm):
    class Meta:
        model = Session
        fields = ['competition','name','time']
        widgets = {'competition': forms.HiddenInput(),
                   'name':forms.TextInput(attrs={'class':'management-input'}),
                   'time':TimeInput(attrs={'class':'management-input'})}

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
        fields = ['session','name','abbreviation']
        widgets = {'session': forms.HiddenInput(),
                   'name':forms.TextInput(attrs={'class':'management-input'}),
                   'abbreviation':forms.TextInput(attrs={'class':'management-input'})}

class AthleteForm(ModelForm):
    class Meta:
        model = Athlete
        fields = ['team','level','name','rotation']
        widgets = {'team': forms.HiddenInput(),
                   'name':forms.TextInput(attrs={'class':'management-input'}),
                   'rotation':forms.TextInput(attrs={'class':'management-input'}),
                   'level':forms.Select(attrs={'class':'selectpicker management-input','data-style':'btn-main'})}
           