from datetime import datetime
import factory

from scheduler.models import Applicant, Application, Interviewer, InterviewSlot, BusyTime, Job, Room


class JobFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Job

    title = factory.sequence(lambda n: f"Job {n}")


class ApplicantFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Applicant

    name = factory.Sequence(lambda n: f"Applicant {n}")


class ApplicationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Application

class BusyTimeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = BusyTime

    begin = datetime(2020, 1, 1, 10)
    end = datetime(2020, 1, 1, 12)


class RoomFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Room

    name = factory.Sequence(lambda n: f"Room {n}")


class InterviewerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Interviewer

    name = factory.Sequence(lambda n: f"Interviewer {n}")


class InterviewSlotFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = InterviewSlot

    start_time = datetime(2020, 1, 1, 10, 0)
    end_time = datetime(2020, 1, 1, 10, 30)
    room = factory.SubFactory(RoomFactory)
