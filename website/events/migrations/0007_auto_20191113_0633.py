# Generated by Django 2.2.6 on 2019-11-13 06:33

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0006_auto_20191113_0631'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event_and_users',
            name='event',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='events.Events'),
        ),
        migrations.AlterField(
            model_name='event_and_users',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
