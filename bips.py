# BIPS: Scheduler class for automatically scheduling interviews
# See management/commands/schedule_interviews.py for use.

import random
import datetime

from uno.app.applications.models import Admission, Applicant, Application, InterviewSlot, BusyTime, Job, Room

TRAVEL_TIME = datetime.timedelta(minutes=30) # represents travel time between rooms


class Interview:
    def __init__(self, applicant, interviewers, interview_slot):
        self.applicant = applicant
        self.interviewers = interviewers
        self.interview_slot = interview_slot

    def __eq__(self, other):
        # Used by unit tests to assert that two Interview objects are equal

        return (isinstance(other, Interview) and
            self.applicant == other.applicant and
            self.interviewers == other.interviewers and
            self.interview_slot == other.interview_slot)

    def print_full(self):
        print()
        print("Applicant: ", self.applicant.name)
        print("Interviewers: ")
        for interviewer in self.interviewers:
            print(interviewer.first_name, interviewer.last_name)
        print("Time: ", self.interview_slot.start_time, "-", self.interview_slot.end_time)
        print("Room: ", self.interview_slot.room)


class Scheduler:
    def __init__(self, seed=0):
        assert_one_interview_slot_per_room_per_time()
        self.applicant_busy_times, self.interviewer_busy_time_space = get_busy_times()
        self.available_interview_slots = set(InterviewSlot.objects.filter(application=None))
        self.applications = get_applications()
        self.applied_jobs = {applicant: [application.job for application in applications]
            for applicant, applications in self.applications.items()}
        self.unallocated_applicants = set(self.applications.keys())
        self.interview_list = []
        random.seed(seed)

    def add_interview(self, applicant, interviewers, interview_slot, index=None):
        if index is None:
            self.interview_list.append(Interview(applicant, interviewers, interview_slot))
        else:
            self.interview_list.insert(index, Interview(applicant, interviewers, interview_slot))
        self.unallocated_applicants.remove(applicant)

        # The interviewers are now busy at this time
        for interviewer in interviewers:
            self.interviewer_busy_time_space.setdefault(interviewer.id, set()).add(
                (interview_slot.start_time, interview_slot.end_time, interview_slot.room))

        # The interviewslot is now taken
        self.available_interview_slots.remove(interview_slot)

    def remove_interview(self, index):
        interview = self.interview_list[index]
        interview_slot = interview.interview_slot
        self.unallocated_applicants.add(interview.applicant)

        # The interviewers are now available at this time
        for interviewer in interview.interviewers:
            self.interviewer_busy_time_space.get(interviewer.id).remove(
                (interview_slot.start_time, interview_slot.end_time, interview_slot.room))

        # The interviewslot is now available
        self.available_interview_slots.add(interview_slot)
        del self.interview_list[index]

    def applicant_is_available(self, applicant, interview_slot):
        if self.applicant_busy_times.get(applicant.id) is None:
            return True
        for busy_time_start, busy_time_end in self.applicant_busy_times.get(applicant.id):
            if (busy_time_start < interview_slot.end_time and
                busy_time_end > interview_slot.start_time):
                return False
        return True

    def interviewer_is_available(self, interviewer, interview_slot):
        start_time = interview_slot.start_time
        end_time = interview_slot.end_time
        if self.interviewer_busy_time_space.get(interviewer.id) is None:
            return True
        for busy_time_start, busy_time_end, busy_room in self.interviewer_busy_time_space.get(
            interviewer.id):
            if busy_room == interview_slot.room or busy_room is None:
                if busy_time_start < end_time and busy_time_end > start_time:
                    return False
            else:
                if (busy_time_start - TRAVEL_TIME < end_time and
                    busy_time_end + TRAVEL_TIME > start_time):
                    return False
        return True

    def get_available_interviewer(self, job, interview_slot, taken_interviewers, must_be_priority_1=False):
        interviewer_lists = [job.possible_interviewers_1, job.possible_interviewers_2,
            job.possible_interviewers_3]
        for interviewer_list_object in interviewer_lists:
            interviewer_list = interviewer_list_object.all()

            # Random order to even out amount of interviews per interviewer
            random_range = list(range(len(interviewer_list)))
            random.shuffle(random_range)

            for i in random_range:
                interviewer = interviewer_list[i]
                if (self.interviewer_is_available(interviewer, interview_slot)
                    and interviewer not in taken_interviewers):
                    return interviewer
            if must_be_priority_1:
                return False
        return False

    def get_available_interviewers(self, jobs, interview_slot):
        # Should be at least two interviewers and at least one interviewer from each job

        interviewers = set()
        for job in jobs:
            interviewer = self.get_available_interviewer(job, interview_slot, interviewers,
                job.include_priority_1_interviewer)
            if interviewer != False:
                interviewers.add(interviewer)
            else:
                return False

        if len(jobs) < 2:
            interviewer = self.get_available_interviewer(jobs[0], interview_slot, interviewers)
            if interviewer != False:
                interviewers.add(interviewer)
            else:
                return False

        return interviewers

    def create_interview(self, applicant):
        jobs = self.applied_jobs[applicant]

        # It's nice to fill up the early interview slots first
        available_interview_slots_sorted = list(self.available_interview_slots)
        available_interview_slots_sorted.sort(key=lambda x : x.start_time)

        for interview_slot in available_interview_slots_sorted:
            if self.applicant_is_available(applicant, interview_slot):
                interviewers = self.get_available_interviewers(jobs, interview_slot)
                if interviewers != False:
                    self.add_interview(applicant, interviewers, interview_slot)
                    return True
        return False

    def take_interview_and_reschedule(self, applicant):
        jobs = self.applied_jobs[applicant]
        for i in range(len(self.interview_list)):
            interview_slot = self.interview_list[i].interview_slot
            if self.applicant_is_available(applicant, interview_slot):
                old_applicant = self.interview_list[i].applicant
                old_jobs = self.applied_jobs[old_applicant]
                old_interviewers = self.interview_list[i].interviewers
                self.remove_interview(i)
                interviewers = self.get_available_interviewers(jobs, interview_slot)
                if interviewers != False:
                    self.add_interview(applicant, interviewers, interview_slot)
                    old_interview_rescheduled = self.create_interview(old_applicant)
                    if old_interview_rescheduled:
                        return
                    else:
                        self.remove_interview(-1)
                self.add_interview(old_applicant, old_interviewers, interview_slot, i)

    def schedule_interviews(self):
        # First, schedule interviews naively
        applicants_to_allocate = set(self.unallocated_applicants)
        for applicant in applicants_to_allocate:
            self.create_interview(applicant)

        # Try to schedule interviews for unallocated applicants by rescheduling other interviews
        applicants_to_allocate = set(self.unallocated_applicants)
        for applicant in applicants_to_allocate:
            self.take_interview_and_reschedule(applicant)

        # Just to be sure, assert that the produced interview list is valid
        assert_interview_list_is_valid(self.interview_list)

    def save_scheduled_interviews(self):
        for interview in self.interview_list:
            for interviewer in interview.interviewers:
                interview.interview_slot.interviewers.add(interviewer)
            interview.interview_slot.save()
            for application in self.applications[interview.applicant]:
                application.interview_slot = interview.interview_slot
                application.save()


def get_busy_times():
    applicant_busy_times = {}
    interviewer_busy_time_space = {}

    for busy_time in BusyTime.objects.all().select_related('applicant', 'interviewer'):
        if busy_time.applicant is not None:
            applicant_busy_times.setdefault(busy_time.applicant.id, set()).add(
                (busy_time.begin, busy_time.end))
        else:
            interviewer_busy_time_space.setdefault(busy_time.interviewer.id, set()).add(
                (busy_time.begin, busy_time.end, None))

    # Interviewers are busy when they are interviewing
    for interview in InterviewSlot.objects.exclude(application=None).select_related(
        'room').prefetch_related('interviewers'):
        for interviewer in interview.interviewers.all():
            interviewer_busy_time_space.setdefault(interviewer.id, set()).add(
                (interview.start_time, interview.end_time, interview.room))

    return applicant_busy_times, interviewer_busy_time_space


def get_applications():
    applied_jobs = {}
    applications_to_allocate = Application.objects.filter(confirmed_interview_slot=False,
        interview_slot=None, withdrawn=False, job__ignore_by_bips=False).select_related(
        'applicant', 'job').prefetch_related('job__possible_interviewers_1',
        'job__possible_interviewers_2', 'job__possible_interviewers_3')
    for application in applications_to_allocate:
        applied_jobs.setdefault(application.applicant, []).append(application)
    return applied_jobs


# Functions for checking database before scheduling interviews

def assert_one_interview_slot_per_room_per_time():
    # This function checks if someone has added overlapping interview slots to the database

    interview_slots = InterviewSlot.objects.all()
    time_slots_for_room = {}
    for interview_slot in interview_slots:
        time_slots_for_room.setdefault(interview_slot.room, []).append(
            (interview_slot.start_time, interview_slot.end_time))

    for room, time_slots in time_slots_for_room.items():
        time_slots_sorted = sorted(time_slots)
        for i in range(len(time_slots_sorted) - 1):
            assert time_slots[i][1] <= time_slots[i+1][0], (
                "The database contains overlapping interview slots for the same room. You need to "
                + "clean this up manually before you can run the scheduler.")


# Functions for validating interview list correctness after scheduling interviews

def assert_interview_list_is_valid(interview_list):
    assert_correct_number_of_interviewers(interview_list)
    assert_applied_jobs_represented_in_interviews(interview_list)
    assert_priority_1_interviewers_when_required(interview_list)
    assert_applicants_available_at_time(interview_list)
    assert_interviewers_available_at_time(interview_list)
    assert_at_most_one_interview_per_interview_slot(interview_list)
    assert_at_most_one_interview_per_interviewer_per_time(interview_list)
    assert_sufficient_travel_time_for_interviewers(interview_list)
    assert_at_most_one_interview_per_applicant(interview_list)


def assert_correct_number_of_interviewers(interview_list):
    for interview in interview_list:
        assert len(interview.interviewers) in {2, 3}


def assert_applied_jobs_represented_in_interviews(interview_list):
    applications = get_applications()
    for interview in interview_list:
        for application in applications[interview.applicant]:
            job = application.job
            assert sum(interviewer in set().union(job.possible_interviewers_1.all(),
                    job.possible_interviewers_2.all(), job.possible_interviewers_3.all())
                for interviewer in interview.interviewers) > 0


def assert_priority_1_interviewers_when_required(interview_list):
    applications = get_applications()
    for interview in interview_list:
        for application in applications[interview.applicant]:
            if application.job.include_priority_1_interviewer:
                assert sum(interviewer in application.job.possible_interviewers_1.all()
                    for interviewer in interview.interviewers) > 0


def assert_applicants_available_at_time(interview_list):
    applicant_busy_times, _ = get_busy_times()
    for interview in interview_list:
        for busy_time_start, busy_time_end in (
            applicant_busy_times.get(interview.applicant.id) or []):
            assert (busy_time_start >= interview.interview_slot.end_time or
                busy_time_end <= interview.interview_slot.start_time)


def assert_interviewers_available_at_time(interview_list):
    _, interviewer_busy_time_space = get_busy_times()
    for interview in interview_list:
        for interviewer in interview.interviewers:
            for busy_time_start, busy_time_end, _ in (
                interviewer_busy_time_space.get(interviewer.id) or []):
                assert (busy_time_start >= interview.interview_slot.end_time or
                    busy_time_end <= interview.interview_slot.start_time)


def assert_at_most_one_interview_per_interview_slot(interview_list):
    interview_slots = [interview.interview_slot for interview in interview_list]
    assert len(interview_slots) == len(set(interview_slots))


def assert_at_most_one_interview_per_interviewer_per_time(interview_list):
    time_slots_for_interviewer = {}
    for interview in interview_list:
        for interviewer in interview.interviewers:
            time_slots_for_interviewer.setdefault(interviewer, []).append(
                (interview.interview_slot.start_time, interview.interview_slot.end_time))

    for _, time_slots in time_slots_for_interviewer.items():
        time_slots_sorted = sorted(time_slots)
        for i in range(len(time_slots_sorted) - 1):
            first_interview_end = time_slots_sorted[i][1]
            second_interview_start = time_slots_sorted[i+1][0]
            assert first_interview_end <= second_interview_start


def assert_sufficient_travel_time_for_interviewers(interview_list):
    time_space_slots_for_interviewer = {}
    for interview in interview_list:
        interview_slot = interview.interview_slot
        for interviewer in interview.interviewers:
            time_space_slots_for_interviewer.setdefault(interviewer, []).append(
                (interview_slot.start_time, interview_slot.end_time, interview_slot.room, False))
    _, interviewer_busy_time_space = get_busy_times()
    for interviewer, busy_time_space in interviewer_busy_time_space.items():
        for start_time, end_time, room in busy_time_space:
            if room is not None:
                time_space_slots_for_interviewer.setdefault(interviewer, []).append(
                    (start_time, end_time, room, True))

    for _, time_space_slots in time_space_slots_for_interviewer.items():
        time_space_slots_sorted = sorted(time_space_slots)
        for i in range(len(time_space_slots_sorted) - 1):
            if time_space_slots_sorted[i][3] and time_space_slots_sorted[i+1][3]:
                # Both where created manually
                continue
            if time_space_slots_sorted[i][2] == time_space_slots_sorted[i+1][2]:
                # The same room, no travel time needed
                continue
            first_interview_end = time_space_slots_sorted[i][1]
            second_interview_start = time_space_slots_sorted[i+1][0]
            assert first_interview_end + TRAVEL_TIME <= second_interview_start


def assert_at_most_one_interview_per_applicant(interview_list):
    applicants = [interview.applicant for interview in interview_list]
    assert len(applicants) == len(set(applicants))

