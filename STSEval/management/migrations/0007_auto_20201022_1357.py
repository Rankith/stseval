# Generated by Django 2.2.16 on 2020-10-22 20:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0006_auto_20201022_1345'),
    ]

    operations = [
        migrations.AlterField(
            model_name='judge',
            name='d1_affil',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AlterField(
            model_name='judge',
            name='d2_affil',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AlterField(
            model_name='judge',
            name='e1_affil',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AlterField(
            model_name='judge',
            name='e2_affil',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AlterField(
            model_name='judge',
            name='e3_affil',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AlterField(
            model_name='judge',
            name='e4_affil',
            field=models.CharField(blank=True, max_length=50),
        ),
    ]
