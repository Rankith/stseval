# Generated by Django 2.2.16 on 2020-10-28 02:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0004_camera_stream'),
    ]

    operations = [
        migrations.AddField(
            model_name='athlete',
            name='order',
            field=models.IntegerField(default=1),
        ),
    ]
