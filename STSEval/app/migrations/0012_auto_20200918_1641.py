# Generated by Django 2.2.16 on 2020-09-18 23:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0011_auto_20200918_1620'),
    ]

    operations = [
        migrations.AddField(
            model_name='routine',
            name='stream_end_time',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='routine',
            name='stream_start_time',
            field=models.IntegerField(default=0),
        ),
    ]
