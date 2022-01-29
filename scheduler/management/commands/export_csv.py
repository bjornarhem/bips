# -*- coding: utf8 -*-

# A management command for exporting interviews to a CSV file.
# Run with python manage.py export_csv in root folder.

import csv
from django.core import management
from scheduler.models import Application, InterviewSlot

class Command(management.BaseCommand):
    help = "Export interviews to CSV"

    def handle(self, *args, **options):
        with open('scheduled_interviews.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Applicant name", "Applicant email", "Start time", "End time",
                "Room", "Interviewers", "Applied jobs"])

            applications = Application.objects.exclude(interview_slot=None).select_related("interview_slot", "applicant", "job")
            interview_slots = {}
            for application in applications:
                interview_slots.setdefault(application.interview_slot, []).append(application)

            for interview_slot in interview_slots:
                related_applications = interview_slots[interview_slot]

                # Assume only one applicant per interview
                applicant_name = related_applications[0].applicant.name
                applicant_email = related_applications[0].applicant.email

                start_time = interview_slot.start_time
                end_time = interview_slot.end_time
                room = interview_slot.room

                interviewer_names = ", ".join([i.name for i in interview_slot.interviewers.all()])

                applied_jobs = ", ".join([app.job.title for app in related_applications])

                writer.writerow(
                    [applicant_name, applicant_email, start_time, end_time, room, interviewer_names, applied_jobs]
                )

