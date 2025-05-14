# utils.py
from datetime import datetime, timedelta

def generate_time_slots(start='09:00', end='17:00', interval_minutes=30):
    slots = []
    start_time = datetime.strptime(start, "%H:%M")
    end_time = datetime.strptime(end, "%H:%M")
    while start_time < end_time:
        slots.append(start_time.strftime("%H:%M"))
        start_time += timedelta(minutes=interval_minutes)
    return slots
