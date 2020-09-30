# Generated by Django 2.2.16 on 2020-09-11 23:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_twitch'),
    ]

    operations = [
        migrations.CreateModel(
            name='StreamMarkers',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('position_seconds_start', models.IntegerField(default=0)),
                ('position_seconds_end', models.IntegerField(default=0)),
            ],
        ),
        migrations.AlterField(
            model_name='twitch',
            name='access_token',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='twitch',
            name='refresh_token',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
