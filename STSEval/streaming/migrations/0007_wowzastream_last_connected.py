# Generated by Django 2.2.16 on 2020-10-19 22:41

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('streaming', '0006_auto_20201019_1132'),
    ]

    operations = [
        migrations.AddField(
            model_name='wowzastream',
            name='last_connected',
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
    ]