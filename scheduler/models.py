# encoding: utf-8

from django.db import models


class Room(models.Model):
    name = models.CharField(verbose_name="Name", max_length=255)

    def __str__(self):
        return self.name


class Applicant(models.Model):
    name = models.CharField(verbose_name="Name", max_length=255)

    def __str__(self):
        return self.name


class Interviewer(models.Model):
    name = models.CharField(verbose_name="Name", max_length=255)

    def __str__(self):
        return self.name


class Job(models.Model):
    title = models.CharField("Job title", max_length=255, unique=True)

    possible_interviewers_1 = models.ManyToManyField(
        Interviewer,
        blank=True,
        related_name="jobs_possible_interviewers_1",
        help_text="Interviewers that can interview for this job, priority 1",
    )
    possible_interviewers_2 = models.ManyToManyField(
        Interviewer,
        blank=True,
        related_name="jobs_possible_interviewers_2",
        help_text="Interviewers that can interview for this job, priority 2",
    )
    possible_interviewers_3 = models.ManyToManyField(
        Interviewer,
        blank=True,
        related_name="jobs_possible_interviewers_3",
        help_text="Interviewers that can interview for this job, priority 3",
    )
    include_priority_1_interviewer = models.BooleanField(
        verbose_name="Interviews must include at least one priority 1 interviewers",
        default=False,
    )

    def __str__(self):
        return self.title


class InterviewSlot(models.Model):
    room = models.ForeignKey(
        Room,
        on_delete=models.PROTECT,
        verbose_name="Room",
    )
    start_time = models.DateTimeField(verbose_name="Start time")
    end_time = models.DateTimeField(verbose_name="End time")
    interviewers = models.ManyToManyField(
        Interviewer,
        verbose_name="Interviewers",
        related_name="interviewing",
        blank=True,
    )


class Application(models.Model):
    applicant = models.ForeignKey(
        Applicant,
        on_delete=models.PROTECT,
        verbose_name="Applicant",
    )
    job = models.ForeignKey(
        Job,
        on_delete=models.PROTECT,
        verbose_name="Job",
    )
    withdrawn = models.BooleanField(default=False, verbose_name="Withdrawn (will be ignored by the interview scheduler)")
    interview_slot = models.ForeignKey(
        InterviewSlot,
        on_delete=models.PROTECT,
        verbose_name="Interview",
        null=True,
        blank=True,
    )


class BusyTime(models.Model):
    """
    A BusyTime object links either an applicant(Applicant) or an interviewer(User) to a start time, an end time
    and possibly a reason
    """

    applicant = models.ForeignKey(
        Applicant,
        on_delete=models.PROTECT,
        verbose_name="Applicant",
        blank=True,
        null=True,
    )
    interviewer = models.ForeignKey(
        Interviewer,
        on_delete=models.PROTECT,
        verbose_name="Interviewer",
        blank=True,
        null=True,
    )
    begin = models.DateTimeField(verbose_name="Start time")
    end = models.DateTimeField(verbose_name="End time")
