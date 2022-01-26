# -*- coding: utf8 -*-

# A management command for automatically scheduling interviews.
# Run with python manage.py schedule_interviews in root folder.

from django.core import management

from scheduler.scheduler import Scheduler


class Command(management.BaseCommand):
    help = 'Automatically schedule interviews for admission'

    def handle(self, *args, **options):
        # Schedule interviews
        scheduler = Scheduler()
        scheduler.schedule_interviews(silent=False)

        print("Scheduled", len(scheduler.interview_list), "interviews.")

        print(len(scheduler.applied_jobs) - len(scheduler.unallocated_applicants), "out of",
            len(scheduler.applied_jobs), "applicants got an interview.")

        # Find and print number of interviews without a priority 1 interviewer for each job
        print("There were",
            sum(0 < sum(not sum(interviewer in job.possible_interviewers_1.all()
            for interviewer in interview.interviewers)
            for job in scheduler.applied_jobs[interview.applicant])
            for interview in scheduler.interview_list),
            "interviews where not all applied jobs had a first priority interviewer present.")

        # Find and print interviewers with more than ten interviews
        num_interviews = {}
        for interview in scheduler.interview_list:
            for interviewer in interview.interviewers:
                num_interviews[interviewer] = num_interviews.setdefault(interviewer, 0) + 1

        print("Interviewers with more than ten interviews:")
        for interviewer in sorted(num_interviews, key = lambda i : num_interviews[i], reverse=True):
            if num_interviews[interviewer] > 10:
                print(interviewer.first_name, interviewer.last_name, ":", num_interviews[interviewer])

        save_interviews = input("Save interviews to database? (y/n)")
        if save_interviews != "y":
            print("Didn't save interviews")
            return

        # Save scheduled interviews to database
        scheduler.save_scheduled_interviews()
        print("Saved interviews.")
