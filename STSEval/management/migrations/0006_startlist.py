# Generated by Django 2.2.16 on 2020-10-28 21:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0005_athlete_order'),
    ]

    operations = [
        migrations.CreateModel(
            name='StartList',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('completed', models.BooleanField(default=False)),
                ('active', models.BooleanField(default=True)),
                ('order', models.IntegerField(default=1)),
                ('athlete', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='management.Athlete')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='management.Event')),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='management.Session')),
            ],
        ),
    ]
