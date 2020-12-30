# Generated by Django 2.2.16 on 2020-12-30 02:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0008_auto_20201229_1837'),
    ]

    operations = [
        migrations.AlterField(
            model_name='purchase',
            name='type',
            field=models.CharField(choices=[('PANEL', 'Panel'), ('SPECTATOR', 'Spectator'), ('ACCESS_CODE', 'Access Code'), ('SCOREBOARD', 'Scoreboard'), ('SPECTATOR_VIA_CODE', 'Spectator Via Code')], default='PANEL', max_length=15),
        ),
    ]
