# Generated by Django 2.2.16 on 2020-09-18 23:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0012_auto_20200918_1641'),
    ]

    operations = [
        migrations.AlterField(
            model_name='routine',
            name='athlete_done_time',
            field=models.BigIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='routine',
            name='d1_done_time',
            field=models.BigIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='routine',
            name='start_time',
            field=models.BigIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='routine',
            name='stream_video_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
