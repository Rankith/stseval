# Generated by Django 2.2.16 on 2020-11-06 22:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0006_startlist'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='athletelevel',
            options={'ordering': ['order']},
        ),
        migrations.AddField(
            model_name='athletelevel',
            name='order',
            field=models.IntegerField(default=1),
        ),
    ]
