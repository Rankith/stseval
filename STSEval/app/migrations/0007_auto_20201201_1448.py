# Generated by Django 2.2.16 on 2020-12-01 22:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0006_auto_20201201_1441'),
    ]

    operations = [
        migrations.RenameField(
            model_name='routine',
            old_name='videofile',
            new_name='video_file',
        ),
    ]