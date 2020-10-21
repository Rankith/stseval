"""
Definition of forms.
"""

from django import forms
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.forms import ModelForm
from management.models import Competition,Session,Athlete,Judge

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
                   'event': forms.HiddenInput()};