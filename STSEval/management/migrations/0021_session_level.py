# Generated by Django 2.2.16 on 2020-12-24 01:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0020_session_paid'),
    ]

    operations = [
        migrations.AddField(
            model_name='session',
            name='level',
            field=models.CharField(choices=[('NCAA', 'NCAA'), ('FIG', 'FIG'), ('USAG', 'USAG'), ('JO', 'JO')], default='NCAA', max_length=6),
        ),
    ]
