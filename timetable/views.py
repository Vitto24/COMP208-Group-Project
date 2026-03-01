import datetime
import math
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from grades.models import Assignment
from .models import TimetableEntry
from .utils import (
    TERM_BLOCKS, get_week_monday, get_current_week,
    get_term_info, get_max_week, parse_weeks, get_current_semester,
)

DAYS = ['MON', 'TUE', 'WED', 'THU', 'FRI']
DAY_NAMES = {
    'MON': 'Monday', 'TUE': 'Tuesday', 'WED': 'Wednesday',
    'THU': 'Thursday', 'FRI': 'Friday',
}
DAY_MAP = {0: 'MON', 1: 'TUE', 2: 'WED', 3: 'THU', 4: 'FRI'}


@login_required
def timetable_view(request):
    semester = get_current_semester()

    # Week navigation
    current_week = get_current_week(semester)
    week_num = int(request.GET.get('week', current_week))
    max_week = get_max_week(semester)
    week_num = max(1, min(week_num, max_week))

    # Dates for the selected week (Mon–Fri)
    week_monday = get_week_monday(semester, week_num)
    week_dates = {}
    if week_monday:
        for i, day in enumerate(DAYS):
            week_dates[day] = week_monday + datetime.timedelta(days=i)

    # Term info for banner
    term_info = get_term_info(semester, week_num)

    # All entries for this semester
    all_entries = TimetableEntry.objects.filter(
        student=request.user, semester=semester
    ).select_related('module')

    # Filter entries that run in the selected week
    week_entries = []
    for entry in all_entries:
        entry_weeks = parse_weeks(entry.weeks)
        if not entry_weeks or week_num in entry_weeks:
            week_entries.append(entry)

    # Build time-slot grid: group entries by hour
    today = datetime.date.today()
    now = datetime.datetime.now().time()
    today_code = DAY_MAP.get(today.weekday(), '')

    is_current_week = week_num == current_week

    # Build grid rows (9:00–17:00, always show all hours)
    hours = list(range(9, 18))
    # Track which cells are occupied by a rowspan from above
    occupied = set()  # (hour_index, day_index)

    grid_rows = []
    for hi, hour in enumerate(hours):
        time_label = f'{hour:02d}:00'
        cells = []
        for di, day in enumerate(DAYS):
            is_today = day == today_code and is_current_week
            if (hi, di) in occupied:
                cells.append({'skip': True})
                continue

            entries = sorted(
                [e for e in week_entries if e.day == day and e.start_time.hour == hour],
                key=lambda e: e.start_time,
            )

            rowspan = 1
            if entries:
                max_minutes = max(
                    (e.end_time.hour * 60 + e.end_time.minute) - (e.start_time.hour * 60 + e.start_time.minute)
                    for e in entries
                )
                rowspan = max(1, math.ceil(max_minutes / 60))
                rowspan = min(rowspan, len(hours) - hi)
                for offset in range(1, rowspan):
                    occupied.add((hi + offset, di))

            cells.append({
                'entries': entries,
                'rowspan': rowspan,
                'skip': False,
                'is_today': is_today,
            })
        grid_rows.append({'time': time_label, 'cells': cells})

    # Day headers with dates and today flag
    day_headers = []
    for day in DAYS:
        day_headers.append({
            'code': day,
            'date': week_dates.get(day),
            'is_today': day == today_code and is_current_week,
        })

    # Today's entries with status (always for current week)
    today_entries = []
    if today_code:
        todays_events = []
        for entry in all_entries:
            if entry.day != today_code:
                continue
            entry_weeks = parse_weeks(entry.weeks)
            if not entry_weeks or current_week in entry_weeks:
                todays_events.append(entry)
        todays_events.sort(key=lambda e: e.start_time)

        for entry in todays_events:
            if now > entry.end_time:
                status = 'done'
            elif entry.start_time <= now <= entry.end_time:
                status = 'now'
            else:
                status = 'upcoming'
            today_entries.append({'entry': entry, 'status': status})

    # Upcoming deadlines (next 5)
    deadlines = Assignment.objects.filter(
        module__students=request.user,
        due_date__gte=today,
    ).select_related('module').order_by('due_date')[:5]

    return render(request, 'timetable/timetable.html', {
        'grid_rows': grid_rows,
        'day_headers': day_headers,
        'today_entries': today_entries,
        'today_date': today,
        'semester': semester,
        'week_num': week_num,
        'current_week': current_week,
        'max_week': max_week,
        'term_info': term_info,
        'deadlines': deadlines,
    })
