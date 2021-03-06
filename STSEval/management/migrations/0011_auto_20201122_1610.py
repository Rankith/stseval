# Generated by Django 2.2.16 on 2020-11-23 00:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0010_auto_20201117_1612'),
    ]

    operations = [
        migrations.AddField(
            model_name='athlete',
            name='events_competing',
            field=models.ManyToManyField(related_name='events_competing_related', to='management.Event'),
        ),
        migrations.AddField(
            model_name='athlete',
            name='events_count_for_team',
            field=models.ManyToManyField(to='management.Event'),
        ),
    ]
