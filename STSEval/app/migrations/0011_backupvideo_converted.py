# Generated by Django 2.2.16 on 2020-12-03 00:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0010_remove_routine_video_file'),
    ]

    operations = [
        migrations.AddField(
            model_name='backupvideo',
            name='converted',
            field=models.BooleanField(default=False),
        ),
    ]
