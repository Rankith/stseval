# Generated by Django 2.2.16 on 2020-12-18 19:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0018_camera_current_event'),
    ]

    operations = [
        migrations.AddField(
            model_name='session',
            name='email_sent',
            field=models.BooleanField(default=False),
        ),
    ]
