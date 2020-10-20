"""
Definition of forms.
"""

from django import forms
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.forms import ModelForm
from management.models import Competition,Session,Athlete

class CompetitionForm(ModelForm):
    class Meta:
        model = Competition
        fields = ['name','type','date']