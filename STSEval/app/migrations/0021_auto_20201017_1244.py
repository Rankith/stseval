# Generated by Django 2.2.16 on 2020-10-17 19:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0020_auto_20201010_1157'),
    ]

    operations = [
        migrations.AddField(
            model_name='routine',
            name='e1_include',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='routine',
            name='e2_include',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='routine',
            name='e3_include',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='routine',
            name='e4_include',
            field=models.BooleanField(default=True),
        ),
    ]