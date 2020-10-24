# Generated by Django 2.2.16 on 2020-10-23 21:54

from django.db import migrations, models
import django.db.models.deletion
import management.models


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0019_camera'),
    ]

    operations = [
        migrations.AlterField(
            model_name='camera',
            name='location',
            field=models.CharField(max_length=50),
        ),
        migrations.CreateModel(
            name='Sponsor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to=management.models.sponsor_path)),
                ('name', models.CharField(max_length=50)),
                ('url', models.URLField(blank=True)),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='management.Session')),
            ],
        ),
    ]