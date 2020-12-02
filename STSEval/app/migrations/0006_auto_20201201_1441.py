# Generated by Django 2.2.16 on 2020-12-01 22:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_routine_score_connection'),
    ]

    operations = [
        migrations.AddField(
            model_name='routine',
            name='videofile',
            field=models.FileField(null=True, upload_to='routine_videos/'),
        ),
        migrations.AlterField(
            model_name='routine',
            name='status',
            field=models.CharField(choices=[('N', 'New'), ('S', 'Started'), ('AD', 'Athlete Done'), ('RD', 'Review Done'), ('F', 'Finished'), ('D', 'Deleted'), ('M', 'Manual')], default='N', max_length=2),
        ),
    ]
