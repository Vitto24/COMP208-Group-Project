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
PANEL_DAYS = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']
DAY_NAMES = {
    'MON': 'Monday', 'TUE': 'Tuesday', 'WED': 'Wednesday',
    'THU': 'Thursday', 'FRI': 'Friday', 'SAT': 'Saturday', 'SUN': 'Sunday',
}
DAY_MAP = {0: 'MON', 1: 'TUE', 2: 'WED', 3: 'THU', 4: 'FRI', 5: 'SAT', 6: 'SUN'}
GRID_DAY_MAP = {0: 'MON', 1: 'TUE', 2: 'WED', 3: 'THU', 4: 'FRI'}


@login_required
def timetable_view(request):
    # Semester switcher: use query param if provided, otherwise auto-detect
    default_semester = get_current_semester()
    try:
        semester = int(request.GET.get('semester', default_semester))
        if semester not in (1, 2):
            semester = default_semester
    except (ValueError, TypeError):
        semester = default_semester

    # Week navigation (reset to week 1 when switching semester)
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

    # Day selector for the "Today" panel: defaults to today (Mon-Sun) in the current week
    default_day = today_code if is_current_week else 'MON'
    selected_day = request.GET.get('day', default_day)
    if selected_day not in PANEL_DAYS:
        selected_day = default_day

    # selected day's date: Mon-Fri come from week_dates; Sat/Sun are offsets from Monday
    if selected_day in week_dates:
        selected_day_date = week_dates[selected_day]
    elif week_monday:
        offset = PANEL_DAYS.index(selected_day)
        selected_day_date = week_monday + datetime.timedelta(days=offset)
    else:
        selected_day_date = None

    viewing_today = (selected_day_date == today)

    # relative label: (Today), (Yesterday), (3 days ago), (Tomorrow), (in 2 days), or none
    relative_label = ''
    if selected_day_date:
        diff = (selected_day_date - today).days
        if diff == 0:
            relative_label = 'Today'
        elif diff == -1:
            relative_label = 'Yesterday'
        elif diff == 1:
            relative_label = 'Tomorrow'
        elif -6 <= diff < -1:
            relative_label = f'{-diff} days ago'
        elif 1 < diff <= 6:
            relative_label = f'in {diff} days'

    # prev/next day codes with week crossing (Sun → next week's Mon, etc.)
    day_idx = PANEL_DAYS.index(selected_day)
    if day_idx > 0:
        prev_day, prev_week = PANEL_DAYS[day_idx - 1], week_num
    elif week_num > 1:
        prev_day, prev_week = PANEL_DAYS[-1], week_num - 1
    else:
        prev_day, prev_week = None, None

    if day_idx < len(PANEL_DAYS) - 1:
        next_day, next_week = PANEL_DAYS[day_idx + 1], week_num
    elif week_num < max_week:
        next_day, next_week = PANEL_DAYS[0], week_num + 1
    else:
        next_day, next_week = None, None

    # Entries for the selected day (only Mon-Fri have any; Sat/Sun always empty)
    day_entries = []
    selected_events = sorted(
        [e for e in week_entries if e.day == selected_day],
        key=lambda e: e.start_time,
    )
    for entry in selected_events:
        if viewing_today:
            if now > entry.end_time:
                status = 'done'
            elif entry.start_time <= now <= entry.end_time:
                status = 'now'
            else:
                status = 'upcoming'
        else:
            status = ''
        day_entries.append({'entry': entry, 'status': status})

    # Upcoming deadlines (next 5)
    deadlines = Assignment.objects.filter(
        module__students=request.user,
        due_date__gte=today,
    ).select_related('module').order_by('due_date')[:5]

    return render(request, 'timetable/timetable.html', {
        'grid_rows': grid_rows,
        'day_headers': day_headers,
        'day_entries': day_entries,
        'selected_day': selected_day,
        'selected_day_date': selected_day_date,
        'viewing_today': viewing_today,
        'relative_label': relative_label,
        'prev_day': prev_day,
        'prev_week': prev_week,
        'next_day': next_day,
        'next_week': next_week,
        'today_code': today_code,
        'today_date': today,
        'semester': semester,
        'week_num': week_num,
        'current_week': current_week,
        'max_week': max_week,
        'term_info': term_info,
        'deadlines': deadlines,
    })
