# Generated by Django 2.2.16 on 2020-11-06 22:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0008_auto_20201106_1411'),
    ]

    operations = [
        migrations.AddField(
            model_name='athletelevel',
            name='scoring_type',
            field=models.CharField(choices=[('JO4567', 'JO4567'), ('JO8910', 'JO8910'), ('FIG', 'FIG')], default='FIG', max_length=10),
        ),
    ]