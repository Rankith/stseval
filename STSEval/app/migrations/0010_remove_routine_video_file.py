# Generated by Django 2.2.16 on 2020-12-03 00:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0009_auto_20201202_1134'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='routine',
            name='video_file',
        ),
    ]
