# Generated by Django 2.2.16 on 2020-12-05 01:21

from django.db import migrations, models

def link_events(apps, schema_editor):
	Routine = apps.get_model('app', 'Routine')
	Event = apps.get_model('management', 'Event')
	for r in Routine.objects.all():
		if(r.event is not None):
			ev = Event.objects.filter(disc = r.session.competition.disc,name=r.event).first()
			r.event_link = ev
			r.save()

class Migration(migrations.Migration):

    dependencies = [
        ('app', '0015_routine_event_link'),
    ]

    operations = [
		migrations.RunPython(link_events),
    ]