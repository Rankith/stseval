# Generated by Django 2.2.16 on 2020-12-24 20:38

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0022_session_payment_id'),
        ('account', '0002_user_stripe_customer'),
    ]

    operations = [
        migrations.CreateModel(
            name='Purchase',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('PA', 'Panel'), ('SP', 'Spectator'), ('AC', 'Access Code'), ('SC', 'Scoreboard')], default='PA', max_length=2)),
                ('quantity', models.IntegerField(default=1)),
                ('stripe_payment', models.CharField(blank=True, default='', max_length=255)),
                ('session', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='management.Session')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
