# Generated by Django 2.2.16 on 2020-10-27 18:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('streaming', '0002_remove_wowzastream_session'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='wowzastream',
            name='disc',
        ),
        migrations.RemoveField(
            model_name='wowzastream',
            name='event',
        ),
    ]
