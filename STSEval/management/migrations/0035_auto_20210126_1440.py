# Generated by Django 2.2.16 on 2021-01-26 22:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0034_auto_20210122_1755'),
    ]

    operations = [
        migrations.AddField(
            model_name='session',
            name='closing_message',
            field=models.CharField(blank=True, default='', max_length=150),
        ),
        migrations.AddField(
            model_name='session',
            name='welcome_message',
            field=models.CharField(blank=True, default='', max_length=150),
        ),
    ]