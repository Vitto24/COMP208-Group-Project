import datetime
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import TimetableEntry

TIME_SLOTS = [
    '09:00', '10:00', '11:00', '12:00',
    '13:00', '14:00', '15:00', '16:00', '17:00',
]

DAYS = ['MON', 'TUE', 'WED', 'THU', 'FRI']
DAY_NAMES = {'MON': 'Monday', 'TUE': 'Tuesday', 'WED': 'Wednesday', 'THU': 'Thursday', 'FRI': 'Friday'}
DAY_MAP = {0: 'MON', 1: 'TUE', 2: 'WED', 3: 'THU', 4: 'FRI'}


@login_required
def timetable_view(request):
    semester = 2  # TODO: make this dynamic
    entries = TimetableEntry.objects.filter(student=request.user, semester=semester)

    # Build grid: for each time slot, a dict of day -> list of entries
    grid = {}
    for slot in TIME_SLOTS:
        grid[slot] = {day: [] for day in DAYS}

    for entry in entries:
        time_key = entry.start_time.strftime('%H:%M')
        if time_key in grid:
            grid[time_key][entry.day].append(entry)

    # Build rows as list of (time, {day: entries}) for the template
    rows = []
    for slot in TIME_SLOTS:
        rows.append((slot, grid[slot]))

    # Today's entries
    today = datetime.date.today()
    today_code = DAY_MAP.get(today.weekday(), '')
    today_name = DAY_NAMES.get(today_code, '')
    today_entries = entries.filter(day=today_code).order_by('start_time') if today_code else []

    return render(request, 'timetable/timetable.html', {
        'rows': rows,
        'today_entries': today_entries,
        'today_name': today_name,
        'semester': semester,
    })
