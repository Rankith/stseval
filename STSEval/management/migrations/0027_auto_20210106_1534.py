# Generated by Django 2.2.16 on 2021-01-06 23:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0026_session_use_ejudge_dots'),
    ]

    operations = [
        migrations.AlterField(
            model_name='session',
            name='level',
            field=models.CharField(choices=[('NCAA', 'NCAA'), ('FIG', 'FIG'), ('USAG', 'USAG'), ('WDP', 'WDP')], default='NCAA', max_length=6),
        ),
    ]