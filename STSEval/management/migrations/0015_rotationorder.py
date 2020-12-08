# Generated by Django 2.2.16 on 2020-12-07 20:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0014_startlist_secondary_judging'),
    ]

    operations = [
        migrations.CreateModel(
            name='RotationOrder',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rotation', models.CharField(default='A', max_length=2)),
                ('order', models.IntegerField(default=1)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='management.Event')),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='management.Session')),
            ],
        ),
    ]