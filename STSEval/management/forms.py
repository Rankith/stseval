"""
Definition of forms.
"""

from django import forms
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.forms import ModelForm
from management.models import Competition,Session,Athlete

class DateInput(forms.DateInput):
    input_type = 'date'

class CompetitionForm(ModelForm):
    class Meta:
        model = Competition
        fields = ['disc','name','type','date']
        widgets = {'disc': forms.HiddenInput(),
                   'name':forms.TextInput(attrs={'class':'management-input'}),
                   'date':DateInput(attrs={'class':'management-input'}),
                   'type':forms.Select(attrs={'class':'selectpicker','data-style':'btn-main'})}