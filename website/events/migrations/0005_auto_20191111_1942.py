# Generated by Django 2.2.6 on 2019-11-11 19:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0004_auto_20191111_1927'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='event_and_users',
            options={'managed': True, 'verbose_name_plural': 'Event_and_users'},
        ),
        migrations.AlterModelTable(
            name='event_and_users',
            table='event_and_users',
        ),
    ]
