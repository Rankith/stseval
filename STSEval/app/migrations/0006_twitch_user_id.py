# Generated by Django 2.2.16 on 2020-09-11 23:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_auto_20200911_1610'),
    ]

    operations = [
        migrations.AddField(
            model_name='twitch',
            name='user_id',
            field=models.CharField(blank=True, max_length=50),
        ),
    ]
