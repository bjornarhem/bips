from django.contrib import admin

from .models import Room, Applicant, Interviewer, Job, InterviewSlot, Application, BusyTime

admin.site.register(Room)
admin.site.register(Applicant)
admin.site.register(Interviewer)
admin.site.register(Job)
admin.site.register(InterviewSlot)
admin.site.register(Application)
admin.site.register(BusyTime)
