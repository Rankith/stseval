# Generated by Django 2.2.16 on 2020-11-20 02:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='routine',
            name='video_converted',
            field=models.BooleanField(default=False),
        ),
    ]
