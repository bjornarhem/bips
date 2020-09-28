from datetime import datetime
from django.test import TestCase

from uno.app.applications.bips import Scheduler, Interview, get_applications, get_busy_times, assert_one_interview_slot_per_room_per_time, assert_interview_list_is_valid
from uno.utils.tests.factory_f import ApplicantFactory, ApplicationFactory, BusyTimeFactory, InterviewSlotFactory, JobFactory, RoomFactory, UserFactory

# Tests for automatic interview scheduling
# Run with python manage.py test uno/app/applications/ (in root folder)


class BasicBipsTest(TestCase):
    def setUp(self):
        # Insert test stuff in the test database
        self.interviewer1 = UserFactory()
        self.interviewer2 = UserFactory()
        self.job1 = JobFactory()
        self.job1.possible_interviewers_1.add(self.interviewer1, self.interviewer2)
        self.applicant1 = ApplicantFactory()
        self.application1 = ApplicationFactory(applicant=self.applicant1, job=self.job1)
        self.room1 = RoomFactory()
        self.interview_slot1 = InterviewSlotFactory(room=self.room1)

        self.scheduler = Scheduler()

    def test_get_applications(self):
        # Verify that the correct applications are returned
        self.job2 = JobFactory(ignore_by_bips=True)
        self.job3 = JobFactory()
        self.application2 = ApplicationFactory(applicant=self.applicant1, job=self.job2)
        self.application3 = ApplicationFactory(applicant=self.applicant1, job=self.job3,
            withdrawn=True)
        self.application4 = ApplicationFactory(applicant=self.applicant1, job=self.job3,
            confirmed_interview_slot=True)
        self.application5 = ApplicationFactory(applicant=self.applicant1, job=self.job3,
            interview_slot=self.interview_slot1)
        applications = {self.applicant1: [self.application1]}
        self.assertEqual(get_applications(), applications)

    def test_get_busy_times(self):
        # TODO: Add test to see that interviews are added as busy time. Need to figure out to way
        # to add reverse foreign key to factory object (application to interview slot).
        self.busy_time1 = BusyTimeFactory(interviewer=self.interviewer1,
            begin=datetime(2020,6,22,10), end=datetime(2020,6,22,11))
        self.busy_time2 = BusyTimeFactory(applicant=self.applicant1,
            begin=datetime(2020,6,21,10), end=datetime(2020,6,21,11))
        busy_times = (
            {self.applicant1.id:
                {(datetime(2020,6,21,10), datetime(2020,6,21,11))}},
            {self.interviewer1.id:
                {(datetime(2020,6,22,10), datetime(2020,6,22,11), None)}}
        )
        self.assertEqual(get_busy_times(), busy_times)

    def test_schedule_interviews(self):
        self.scheduler.schedule_interviews()
        interview_list = [Interview(self.applicant1, {self.interviewer2, self.interviewer1},
            self.interview_slot1)]
        self.assertEqual(self.scheduler.interview_list, interview_list)

    def test_busy_times_are_updated(self):
        # Test that generated interviews are added to stored as busy-time-spaces for interviewers
        self.scheduler.add_interview(self.applicant1, {self.interviewer1, self.interviewer2},
            self.interview_slot1)
        busy_time_space = {(self.interview_slot1.start_time, self.interview_slot1.end_time,
            self.interview_slot1.room)}
        interviewer_busy_time_space = {
            self.interviewer1.id: busy_time_space,
            self.interviewer2.id: busy_time_space
        }
        self.assertEqual(self.scheduler.interviewer_busy_time_space, interviewer_busy_time_space)

    def test_save_scheduled_interviews(self):
        self.scheduler.schedule_interviews()
        interview_list = [Interview(self.applicant1, {self.interviewer2, self.interviewer1},
            self.interview_slot1)]
        self.assertEqual(self.scheduler.interview_list, interview_list)
        self.scheduler.save_scheduled_interviews()
        self.assertEqual(get_applications(), {})


class BipsReschedulingTest(TestCase):
    def setUp(self):
        # Insert test stuff in the test database
        self.interviewer1 = UserFactory()
        self.interviewer2 = UserFactory()
        self.job1 = JobFactory()
        self.job1.possible_interviewers_1.add(self.interviewer1, self.interviewer2)
        self.applicant1 = ApplicantFactory()
        self.applicant2 = ApplicantFactory()
        self.application1 = ApplicationFactory(applicant=self.applicant1, job=self.job1)
        self.application2 = ApplicationFactory(applicant=self.applicant2, job=self.job1)
        self.room1 = RoomFactory()
        self.interview_slot1 = InterviewSlotFactory(room=self.room1,
            start_time=datetime(2020,6,21,10,0),
            end_time=datetime(2020,6,21,10,30))
        self.interview_slot2 = InterviewSlotFactory(room=self.room1,
            start_time=datetime(2020,6,21,10,30),
            end_time=datetime(2020,6,21,11,0))
        self.busy_time1 = BusyTimeFactory(applicant=self.applicant2,
            begin=datetime(2020,6,21,10,30), end=datetime(2020,6,21,11,0))

        self.scheduler = Scheduler()
        self.scheduler.add_interview(self.applicant1, {self.interviewer1, self.interviewer2},
            self.interview_slot1)

    def test_re_schedule_interviews(self):
        self.scheduler.schedule_interviews()
        interviewers = {self.interviewer1, self.interviewer2}
        interview_list = [Interview(self.applicant1, interviewers, self.interview_slot2),
            Interview(self.applicant2, interviewers, self.interview_slot1)]
        self.assertCountEqual(self.scheduler.interview_list, interview_list)


class BipsDatabaseValidationTest(TestCase):
    def setUp(self):
        self.room1 = RoomFactory()
        self.interview_slot1 = InterviewSlotFactory(room=self.room1,
            start_time=datetime(2020,7,12,10,0),
            end_time=datetime(2020,7,12,10,30))
        self.interview_slot2 = InterviewSlotFactory(room=self.room1,
            start_time=datetime(2020,7,12,10,15),
            end_time=datetime(2020,7,12,10,45))

    def test_assert_one_interview_slot_per_room_per_time(self):
        with self.assertRaises(AssertionError):
            assert_one_interview_slot_per_room_per_time()


class BipsInterviewListValidationTest(TestCase):
    def setUp(self):
        self.interviewer1 = UserFactory()
        self.interviewer2 = UserFactory()
        self.job1 = JobFactory()
        self.job1.possible_interviewers_1.add(self.interviewer1, self.interviewer2)
        self.applicant1 = ApplicantFactory()
        self.applicant2 = ApplicantFactory()
        self.application1 = ApplicationFactory(applicant=self.applicant1, job=self.job1)
        self.application2 = ApplicationFactory(applicant=self.applicant2, job=self.job1)
        self.room1 = RoomFactory()
        self.interview_slot1 = InterviewSlotFactory(start_time=datetime(2020,7,12,10,0),
            end_time=datetime(2020,7,12,10,30), room=self.room1)

    def test_assert_correct_number_of_interviewers(self):
        interview_list = [Interview(self.applicant1, {self.interviewer1}, self.interview_slot1)]
        with self.assertRaises(AssertionError):
            assert_interview_list_is_valid(interview_list)

    def test_assert_applied_jobs_represented_in_interviews(self):
        self.job2 = JobFactory()
        self.application2 = ApplicationFactory(applicant=self.applicant1, job=self.job2)
        interview_list = [Interview(
            self.applicant1, {self.interviewer1, self.interviewer2}, self.interview_slot1)]
        with self.assertRaises(AssertionError):
            assert_interview_list_is_valid(interview_list)

    def test_assert_priority_1_interviewers_when_required(self):
        self.interviewer3 = UserFactory()
        self.interviewer4 = UserFactory()
        self.job1.include_priority_1_interviewer = True
        self.job1.possible_interviewers_2.add(self.interviewer3, self.interviewer4)
        self.job1.save()
        interview_list = [Interview(
            self.applicant1, {self.interviewer3, self.interviewer4}, self.interview_slot1)]
        with self.assertRaises(AssertionError):
            assert_interview_list_is_valid(interview_list)

    def test_assert_applicants_available_at_time(self):
        self.busy_time1 = BusyTimeFactory(applicant=self.applicant1,
            begin=datetime(2020,7,12,10,0), end=datetime(2020,7,12,11,0))
        interview_list = [Interview(
            self.applicant1, {self.interviewer1, self.interviewer2}, self.interview_slot1)]
        with self.assertRaises(AssertionError):
            assert_interview_list_is_valid(interview_list)

    def test_assert_interviewers_available_at_time(self):
        self.busy_time1 = BusyTimeFactory(interviewer=self.interviewer1,
            begin=datetime(2020,7,12,10,0), end=datetime(2020,7,12,11,0))
        interview_list = [Interview(
            self.applicant1, {self.interviewer1, self.interviewer2}, self.interview_slot1)]
        with self.assertRaises(AssertionError):
            assert_interview_list_is_valid(interview_list)

    def test_assert_at_most_one_interview_per_interview_slot(self):
        interviewers = {self.interviewer1, self.interviewer2}
        interview_list = [Interview(self.applicant1, interviewers, self.interview_slot1),
            Interview(self.applicant2, interviewers, self.interview_slot1)]
        with self.assertRaises(AssertionError):
            assert_interview_list_is_valid(interview_list)

    def test_assert_at_most_one_interview_per_interviewer_per_time(self):
        self.interview_slot2 = InterviewSlotFactory(start_time=datetime(2020,7,12,10,0),
            end_time=datetime(2020,7,12,10,30))
        interviewers = {self.interviewer1, self.interviewer2}
        interview_list = [Interview(self.applicant1, interviewers, self.interview_slot1),
            Interview(self.applicant2, interviewers, self.interview_slot2)]
        with self.assertRaises(AssertionError):
            assert_interview_list_is_valid(interview_list)

    def test_assert_sufficient_travel_time_for_interviewers(self):
        self.interview_slot2 = InterviewSlotFactory(start_time=datetime(2020,7,12,10,30),
            end_time=datetime(2020,7,12,11,0))
        interviewers = {self.interviewer1, self.interviewer2}
        interview_list = [Interview(self.applicant1, interviewers, self.interview_slot1),
            Interview(self.applicant2, interviewers, self.interview_slot2)]
        with self.assertRaises(AssertionError):
            assert_interview_list_is_valid(interview_list)

    def test_assert_at_most_one_interview_per_applicant(self):
        self.interview_slot2 = InterviewSlotFactory(start_time=datetime(2020,7,12,10,30),
            end_time=datetime(2020,7,12,11,0), room=self.room1)
        interviewers = {self.interviewer1, self.interviewer2}
        interview_list = [Interview(self.applicant1, interviewers, self.interview_slot1),
            Interview(self.applicant1, interviewers, self.interview_slot2)]
        with self.assertRaises(AssertionError):
            assert_interview_list_is_valid(interview_list)


class BipsSimpleSchedulingScenariosTest(TestCase):
    def setUp(self):
        self.interviewer1 = UserFactory()
        self.interviewer2 = UserFactory()
        self.job1 = JobFactory()
        self.job1.possible_interviewers_1.add(self.interviewer1)
        self.job1.possible_interviewers_2.add(self.interviewer2)
        self.applicant1 = ApplicantFactory()
        self.applicant2 = ApplicantFactory()
        self.application1 = ApplicationFactory(applicant=self.applicant1, job=self.job1)
        self.room1 = RoomFactory()
        self.interview_slot1 = InterviewSlotFactory(start_time=datetime(2020,7,12,10,0),
            end_time=datetime(2020,7,12,10,30), room=self.room1)

    def test_basic_scheduling(self):
        scheduler = Scheduler()
        scheduler.schedule_interviews()
        interview_list = [Interview(self.applicant1, {self.interviewer1, self.interviewer2},
            self.interview_slot1)]
        self.assertEqual(scheduler.interview_list, interview_list)

    def test_not_enough_possible_interviewers(self):
        self.job1.possible_interviewers_1.remove(self.interviewer1)
        scheduler = Scheduler()
        scheduler.schedule_interviews()
        self.assertEqual(scheduler.interview_list, [])

    def test_no_possible_interviewers(self):
        self.job2 = JobFactory()
        self.application2 = ApplicationFactory(applicant=self.applicant1, job=self.job2)
        scheduler = Scheduler()
        scheduler.schedule_interviews()
        self.assertEqual(scheduler.interview_list, [])

    def test_not_enough_priority_1_possible_interviewers(self):
        self.job1.possible_interviewers_1.remove(self.interviewer1)
        self.job1.possible_interviewers_2.add(self.interviewer1)
        self.job1.include_priority_1_interviewer = True
        self.job1.save()
        scheduler = Scheduler()
        scheduler.schedule_interviews()
        self.assertEqual(scheduler.interview_list, [])

    def test_applicant_busy(self):
        self.busy_time1 = BusyTimeFactory(applicant=self.applicant1,
            begin=datetime(2020,7,12,10,0), end=datetime(2020,7,12,11,0))
        scheduler = Scheduler()
        scheduler.schedule_interviews()
        self.assertEqual(scheduler.interview_list, [])

    def test_interviewer_busy(self):
        self.busy_time1 = BusyTimeFactory(interviewer=self.interviewer1,
            begin=datetime(2020,7,12,10,0), end=datetime(2020,7,12,11,0))
        scheduler = Scheduler()
        scheduler.schedule_interviews()
        self.assertEqual(scheduler.interview_list, [])

    def test_not_enough_interview_slots(self):
        self.application2 = ApplicationFactory(applicant=self.applicant2, job=self.job1)
        scheduler = Scheduler()
        scheduler.schedule_interviews()
        self.assertEqual(len(scheduler.interview_list), 1)

    def test_not_enough_interviewers_or_interview_times(self):
        self.application2 = ApplicationFactory(applicant=self.applicant2, job=self.job1)
        self.interview_slot2 = InterviewSlotFactory(start_time=datetime(2020,7,12,10,0),
            end_time=datetime(2020,7,12,10,30))
        scheduler = Scheduler()
        scheduler.schedule_interviews()
        self.assertEqual(len(scheduler.interview_list), 1)

    def test_insufficient_travel_time(self):
        self.application2 = ApplicationFactory(applicant=self.applicant2, job=self.job1)
        self.interview_slot2 = InterviewSlotFactory(start_time=datetime(2020,7,12,10,30),
            end_time=datetime(2020,7,12,11,0))
        scheduler = Scheduler()
        scheduler.schedule_interviews()
        self.assertEqual(len(scheduler.interview_list), 1)

    def test_three_jobs(self):
        self.interviewer3 = UserFactory()
        self.interviewer4 = UserFactory()
        self.job2 = JobFactory()
        self.job3 = JobFactory()
        self.job2.possible_interviewers_1.add(self.interviewer3)
        self.job3.possible_interviewers_1.add(self.interviewer4)
        self.application2 = ApplicationFactory(applicant=self.applicant1, job=self.job2)
        self.application3 = ApplicationFactory(applicant=self.applicant1, job=self.job3)
        interviewers = {self.interviewer1, self.interviewer3, self.interviewer4}
        scheduler = Scheduler()
        scheduler.schedule_interviews()
        interview_list = [Interview(self.applicant1, interviewers, self.interview_slot1)]
        self.assertEqual(scheduler.interview_list, interview_list)

