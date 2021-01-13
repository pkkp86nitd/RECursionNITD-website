# Generated by Django 2.2.6 on 2019-11-04 17:40

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import interview_exp.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Experiences',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company', models.CharField(max_length=100)),
                ('year', models.PositiveIntegerField(default=2019, validators=[django.core.validators.MinValueValidator(1984), interview_exp.models.max_value_current_year])),
                ('job_Profile', models.CharField(max_length=100)),
                ('no_of_Rounds', models.PositiveIntegerField(default=1, validators=[django.core.validators.MinValueValidator(1)])),
                ('interview_Questions', models.TextField()),
                ('total_Compensation', models.PositiveIntegerField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Experiences',
                'db_table': 'experiences',
                'ordering': ['-created_at'],
                'managed': True,
            },
        ),
    ]