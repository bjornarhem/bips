# -*- coding: utf8 -*-

# A management command for exporting interviews to a CSV file.
# Run with python manage.py export_csv in root folder.

import csv
from django.core import management
from scheduler.models import Application

class Command(management.BaseCommand):
    help = "Export interviews to CSV"

    def handle(self, *args, **options):
        applications_with_interview = Application.objects.exclude(interview_slot=None)
        with open('scheduled_interviews.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Applicant name", "Applicant email", "Start time", "End time",
                "Room", "Interviewer 1", "Interviewer 2", "Interviewer 3"])
            for application in applications_with_interview:
                applicant_name = application.applicant.name
                applicant_email = application.applicant.email
                start_time = application.interview_slot.start_time
                end_time = application.interview_slot.end_time
                room = application.interview_slot.room
                interview_names = [i.name for i in application.interview_slot.interviewers.all()]
                writer.writerow([applicant_name, applicant_email, start_time, end_time, room] + interview_names)

