# Generated by Django 2.2.16 on 2020-12-24 03:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0021_session_level'),
    ]

    operations = [
        migrations.AddField(
            model_name='session',
            name='payment_id',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
    ]