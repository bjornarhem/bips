# A script for uploading applicants and applications to the database from a CSV file
# Usage: python manage.py shell < orbit_scripts/upload_applications.py

FILEPATH="./applicants.csv" # Edit this before using

import csv
from scheduler.models import Applicant, Application, Job

with open(FILEPATH) as csvfile:
    applicants = csv.reader(csvfile)
    next(applicants)
    for row in applicants:
        applicant = Applicant(name=row[1], email=row[2], phone=row[4])
        applicant.save()
        jobs = row[7].split(",")
        for job_title in jobs:
            job_title = job_title.strip()
            existing_jobs = Job.objects.filter(title=job_title)
            if len(existing_jobs) == 0:
                job = Job(title=job_title)
                job.save()
            else:
                job = existing_jobs[0]
            application = Application(applicant=applicant, job=job)
            application.save()

