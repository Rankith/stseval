# Generated by Django 2.2.16 on 2020-11-20 02:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_routine_video_converted'),
    ]

    operations = [
        migrations.AddField(
            model_name='routine',
            name='video_saved',
            field=models.BooleanField(default=False),
        ),
    ]
