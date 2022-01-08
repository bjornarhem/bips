# Generated by Django 3.2.11 on 2022-01-08 21:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Applicant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
            ],
        ),
        migrations.CreateModel(
            name='Interviewer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
            ],
        ),
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
            ],
        ),
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, unique=True, verbose_name='Job title')),
                ('include_priority_1_interviewer', models.BooleanField(default=False, verbose_name='Interviews must include at least one priority 1 interviewers')),
                ('possible_interviewers_1', models.ManyToManyField(blank=True, help_text='Interviewers that can interview for this job, priority 1', related_name='jobs_possible_interviewers_1', to='scheduler.Interviewer')),
                ('possible_interviewers_2', models.ManyToManyField(blank=True, help_text='Interviewers that can interview for this job, priority 2', related_name='jobs_possible_interviewers_2', to='scheduler.Interviewer')),
                ('possible_interviewers_3', models.ManyToManyField(blank=True, help_text='Interviewers that can interview for this job, priority 3', related_name='jobs_possible_interviewers_3', to='scheduler.Interviewer')),
            ],
        ),
        migrations.CreateModel(
            name='InterviewSlot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.DateTimeField(verbose_name='Start time')),
                ('end_time', models.DateTimeField(verbose_name='End time')),
                ('interviewers', models.ManyToManyField(blank=True, related_name='interviewing', to='scheduler.Interviewer', verbose_name='Interviewers')),
                ('room', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='scheduler.room', verbose_name='Room')),
            ],
        ),
        migrations.CreateModel(
            name='BusyTime',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('begin', models.DateTimeField(verbose_name='Start time')),
                ('end', models.DateTimeField(verbose_name='End time')),
                ('applicant', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='scheduler.applicant', verbose_name='Applicant')),
                ('interviewer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='scheduler.interviewer', verbose_name='Interviewer')),
            ],
        ),
        migrations.CreateModel(
            name='Application',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('withdrawn', models.BooleanField(default=False)),
                ('applicant', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='scheduler.applicant', verbose_name='Applicant')),
                ('interview_slot', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='scheduler.interviewslot', verbose_name='Interview')),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='scheduler.job', verbose_name='Job')),
            ],
        ),
    ]
