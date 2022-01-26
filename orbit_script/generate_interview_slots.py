from scheduler.models import Room, InterviewSlot
import datetime

for i in range(10):
    room = Room(name="Digitalt")
    room.save()

for room in Room.objects.all():
    date = datetime.date(2022,2,1) # Edit this
    while date <= datetime.date(2022,2,8): # And this
        first_time = datetime.time(hour=9, minute=15) # And this
        last_time = datetime.time(hour=19, minute=45) # And this
        start_datetime = datetime.datetime.combine(date, first_time)
        last_datetime = datetime.datetime.combine(date, last_time)
        while start_datetime <= last_datetime:
            end_datetime = start_datetime + datetime.timedelta(minutes=45) # And this
            slot = InterviewSlot(start_time=start_datetime, end_time=end_datetime, room=room)
            slot.save()
            start_datetime = end_datetime
        date = date + datetime.timedelta(days=1)

