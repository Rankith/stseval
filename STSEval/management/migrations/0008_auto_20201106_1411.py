# Generated by Django 2.2.16 on 2020-11-06 22:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0007_auto_20201106_1407'),
    ]

    operations = [
        migrations.AlterField(
            model_name='athletelevel',
            name='abbreviation',
            field=models.CharField(blank=True, max_length=14),
        ),
    ]
