from datetime import datetime
import factory

from uno.app.applications.models import Applicant, Application, InterviewSlot, BusyTime, Job, Room
from uno.authentication.models import Group, User


class GroupFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Group

    name = factory.Sequence(lambda n: f"Group {n}")
    type = 3 # Gjeng


class JobFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Job

    title = factory.sequence(lambda n: f"Job {n}")
    group = factory.SubFactory(GroupFactory)


class ApplicantFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Applicant

    email = factory.Sequence(lambda n: f"studentesen{n}@stud.ntnu.no")
    phone = factory.Sequence(lambda n: 40000000 + n)
    school = 10 # Gløs


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


class InterviewSlotFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = InterviewSlot

    start_time = datetime(2020, 1, 1, 10, 0)
    end_time = datetime(2020, 1, 1, 10, 30)
    room = factory.SubFactory(RoomFactory)


class UserFactory(factory.django.DjangoModelFactory): # Interviewers are users.
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"funkesen{n}")
    email = factory.Sequence(lambda n: f"funkesen{n}@samfundet.no")
