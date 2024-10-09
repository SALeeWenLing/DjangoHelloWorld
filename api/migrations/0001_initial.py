# Generated by Django 5.1.2 on 2024-10-09 17:35

import django.db.models.deletion
import django.utils.timezone
import simple_history.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='DevelopmentTag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Sprint',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sprint_name', models.CharField(max_length=100)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('status', models.CharField(choices=[('Inactive', 'Inactive'), ('Active', 'Active'), ('Completed', 'Completed')], default='Inactive', max_length=10)),
                ('activated', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='ModeSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mode', models.CharField(choices=[('dark', 'Dark'), ('light', 'Light')], default='light', max_length=12)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Mode setting',
                'verbose_name_plural': 'Mode settings',
            },
        ),
        migrations.CreateModel(
            name='HistoricalTask',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('task_name', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('priority', models.CharField(choices=[('Low', 'Low'), ('Medium', 'Medium'), ('Important', 'Important'), ('Urgent', 'Urgent')], default='Medium', max_length=9)),
                ('story_point', models.IntegerField()),
                ('done', models.BooleanField(default=False)),
                ('status', models.CharField(choices=[('Not Started', 'Not Started'), ('In Progress', 'In Progress'), ('Completed', 'Completed')], default='Not Started', max_length=20)),
                ('task_stage', models.CharField(choices=[('Project Planning', 'Project Planning'), ('Development', 'Development'), ('Testing', 'Testing'), ('Integration', 'Integration')], default='Project Planning', max_length=16)),
                ('task_type', models.CharField(choices=[('Bug', 'Bug'), ('User Story', 'User Story')], default='User Story', max_length=16)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('assignee', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('sprint', models.ForeignKey(blank=True, db_constraint=False, default=None, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='api.sprint')),
            ],
            options={
                'verbose_name': 'historical task',
                'verbose_name_plural': 'historical tasks',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('task_name', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('priority', models.CharField(choices=[('Low', 'Low'), ('Medium', 'Medium'), ('Important', 'Important'), ('Urgent', 'Urgent')], default='Medium', max_length=9)),
                ('story_point', models.IntegerField()),
                ('done', models.BooleanField(default=False)),
                ('status', models.CharField(choices=[('Not Started', 'Not Started'), ('In Progress', 'In Progress'), ('Completed', 'Completed')], default='Not Started', max_length=20)),
                ('task_stage', models.CharField(choices=[('Project Planning', 'Project Planning'), ('Development', 'Development'), ('Testing', 'Testing'), ('Integration', 'Integration')], default='Project Planning', max_length=16)),
                ('task_type', models.CharField(choices=[('Bug', 'Bug'), ('User Story', 'User Story')], default='User Story', max_length=16)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('assignee', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('development_tag', models.ManyToManyField(to='api.developmenttag')),
                ('sprint', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='api.sprint')),
            ],
        ),
        migrations.CreateModel(
            name='ThemeSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('theme', models.CharField(choices=[('deadpool', 'Deadpool'), ('bubblegum', 'Bubblegum'), ('ocean', 'Ocean'), ('nature', 'Nature')], default='default', max_length=12)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Theme setting',
                'verbose_name_plural': 'Theme settings',
            },
        ),
        migrations.CreateModel(
            name='TimeLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time_spent', models.IntegerField()),
                ('date', models.DateField()),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.task')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
