# Generated by Django 2.2.16 on 2020-10-22 22:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0012_athlete_level'),
    ]

    operations = [
        migrations.AlterField(
            model_name='athletelevel',
            name='abbreviation',
            field=models.CharField(blank=True, max_length=6),
        ),
    ]
