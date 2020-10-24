# Generated by Django 2.2.16 on 2020-10-23 18:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0013_auto_20201022_1519'),
    ]

    operations = [
        migrations.CreateModel(
            name='Disc',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=10)),
                ('full_name', models.CharField(max_length=50)),
                ('active', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('full_name', models.CharField(max_length=50)),
                ('disc', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='management.Disc')),
            ],
        ),
        migrations.RemoveField(
            model_name='judge',
            name='event',
        ),
    ]