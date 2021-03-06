# Generated by Django 2.2.6 on 2019-11-04 17:40

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import user_profile.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('college', models.CharField(max_length=100)),
                ('role', models.CharField(choices=[('1', 'Superuser'), ('2', 'Member'), ('3', 'User')], default='3', max_length=50)),
                ('dept', models.CharField(blank=True, max_length=20, null=True)),
                ('image_url', models.URLField(blank=True, null=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to=user_profile.models.content_file_name)),
                ('email_confirmed', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'managed': True,
            },
        ),
    ]
