# Generated by Django 2.2.16 on 2020-12-04 20:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0011_backupvideo_converted'),
    ]

    operations = [
        migrations.AddField(
            model_name='routine',
            name='video_file',
            field=models.FileField(null=True, upload_to=''),
        ),
    ]