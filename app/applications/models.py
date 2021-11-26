# encoding: utf-8
from __future__ import unicode_literals

import datetime
from django.db import models
from uno.authentication.models import Group, User
from uno.utils.choices import SCHOOLS


class Room(models.Model):
    name = models.CharField('Navn', max_length=40)
    description = models.TextField('Beskrivelse')


class Applicant(models.Model):
    name = models.CharField(max_length=150, verbose_name="navn")
    email = models.EmailField(max_length=150, unique=True, verbose_name="epost")
    phone = models.CharField(max_length=20, verbose_name="telefon")
    school = models.IntegerField(verbose_name="skole", blank=False, null=True,
                                 choices=SCHOOLS)


class Job(models.Model):
    title = models.CharField(max_length=100, unique=True)
    group = models.ForeignKey(Group, related_name='jobs', on_delete = models.PROTECT)
    possible_interviewers_1 = models.ManyToManyField(User, related_name="jobs_possible_interviewers_1",
                                                  blank=True,
                                                  help_text="Brukere som kan være intervjuere, prioritet 1") 
    possible_interviewers_2 = models.ManyToManyField(User, related_name="jobs_possible_interviewers_2",
                                                  blank=True,
                                                  help_text="Brukere som kan være intervjuere, prioritet 2") 
    possible_interviewers_3 = models.ManyToManyField(User, related_name="jobs_possible_interviewers_3",
                                                  blank=True,
                                                  help_text="Brukere som kan være intervjuere, prioritet 3") 
    include_priority_1_interviewer = models.BooleanField(verbose_name='Må være minst en intervjuer med prioritet 1 på intervjuet', default=False)
    ignore_by_bips = models.BooleanField(verbose_name='Skal ignoreres av automatisk intervjufordeling (f.eks. fordi gjengen har egne intervjuer)', default=False)


class InterviewSlot(models.Model):
    room = models.ForeignKey(Room, verbose_name='Rom', on_delete=models.CASCADE)
    start_time = models.DateTimeField('Starttid')
    end_time = models.DateTimeField('Sluttid', null=True)
    interviewers = models.ManyToManyField(User, related_name="interviewing", blank=True)

    def save(self, old_applications=None, old_interviewers=None, *args, **kwargs):
        super(InterviewSlot, self).save(*args, **kwargs)
        # code removed for github upload, normally creates interview mails and
        # store them in the database for sending later


class Application(models.Model):
    applicant = models.ForeignKey(Applicant, verbose_name='Søker', related_name="applications", on_delete = models.PROTECT)
    job = models.ForeignKey(Job, related_name="applications", on_delete = models.PROTECT)
    withdrawn = models.BooleanField(default=False)

    interview_slot = models.ForeignKey(InterviewSlot, verbose_name='Intervju', null=True, blank=True, on_delete = models.PROTECT)
    confirmed_interview_slot = models.BooleanField(default=False)


class BusyTime(models.Model):
    """
    A BusyTime object links either an applicant(Applicant) or an interviewer(User) to a start time, an end time
    and possibly a reason
    """

    applicant = models.ForeignKey(Applicant, related_name="busy_times", verbose_name='Søker', blank=True, null=True, on_delete = models.CASCADE)
    interviewer = models.ForeignKey(User, related_name='busy_times', verbose_name='Intervjuer', blank=True, null=True, on_delete = models.CASCADE)
    begin = models.DateTimeField('Start')
    end = models.DateTimeField('Slutt')
