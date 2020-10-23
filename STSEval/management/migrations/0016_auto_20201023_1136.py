# Generated by Django 2.2.16 on 2020-10-23 18:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0015_judge_event'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='disc',
            options={'ordering': ['display_order']},
        ),
        migrations.AlterModelOptions(
            name='event',
            options={'ordering': ['display_order']},
        ),
        migrations.AddField(
            model_name='disc',
            name='display_order',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='event',
            name='display_order',
            field=models.IntegerField(default=1),
        ),
    ]
