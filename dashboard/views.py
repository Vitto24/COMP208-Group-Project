from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from modules.models import Module
from grades.models import Assignment
from timetable.models import TimetableEntry
from timetable.utils import (
    get_current_semester, get_current_week, get_week_monday,
    get_max_week, parse_weeks,
)
from django.utils import timezone
from datetime import timedelta
import datetime

DEADLINE_WARNING_DAYS = 3
DUE_SOON_DAYS = 7

DAYS = ['MON', 'TUE', 'WED', 'THU', 'FRI']
DAY_MAP = {0: 'MON', 1: 'TUE', 2: 'WED', 3: 'THU', 4: 'FRI'}


@login_required
def dashboard(request):
    semester = get_current_semester()
    modules = Module.objects.filter(
        students=request.user,
        semester=semester,
        academic_year='2025/26',
    )

    now = timezone.now()
    warning_cutoff = now + timedelta(days=DEADLINE_WARNING_DAYS)
    due_soon_cutoff = now + timedelta(days=DUE_SOON_DAYS)

    assignments = Assignment.objects.filter(
        module__students=request.user,
        module__semester=semester,
        module__academic_year='2025/26',
        due_date__gte=now,
    ).order_by('due_date')

    # ── Timetable: week navigation ─────────────────────────────────
    current_week = get_current_week(semester)
    week_num = int(request.GET.get('week', current_week))
    max_week = get_max_week(semester)
    week_num = max(1, min(week_num, max_week))

    # get Mon-Fri dates for the selected week
    week_monday = get_week_monday(semester, week_num)
    week_dates = {}
    if week_monday:
        for i, day in enumerate(DAYS):
            week_dates[day] = week_monday + datetime.timedelta(days=i)

    # ── Timetable: fetch all entries for this semester ──────────────
    all_entries = TimetableEntry.objects.filter(
        student=request.user, semester=semester,
    ).select_related('module')

    # filter to entries that run in the selected week
    week_entries = []
    for entry in all_entries:
        entry_weeks = parse_weeks(entry.weeks)
        if not entry_weeks or week_num in entry_weeks:
            week_entries.append(entry)

    # ── Timetable: build day columns for the mini grid ──────────────
    today = datetime.date.today()
    today_code = DAY_MAP.get(today.weekday(), '')
    is_current_week = week_num == current_week

    day_columns = []
    for day in DAYS:
        # get entries for this day, sorted by start time
        day_entries = sorted(
            [e for e in week_entries if e.day == day],
            key=lambda e: e.start_time,
        )
        day_columns.append({
            'code': day,
            'date': week_dates.get(day),
            'entries': day_entries,
            'is_today': day == today_code and is_current_week,
        })

    # ── Timetable: today's events with done/now/upcoming status ─────
    today_entries = []
    current_time = datetime.datetime.now().time()

    # find today's entries (always use current week, not selected week)
    for entry in all_entries:
        if entry.day != today_code:
            continue
        entry_weeks = parse_weeks(entry.weeks)
        if not entry_weeks or current_week in entry_weeks:
            if entry.end_time <= current_time:
                status = 'done'
            elif entry.start_time <= current_time:
                status = 'now'
            else:
                status = 'upcoming'
            today_entries.append({'entry': entry, 'status': status})

    # sort by start time
    today_entries.sort(key=lambda x: x['entry'].start_time)

    return render(request, 'dashboard/dashboard.html', {
        'modules': modules,
        'assignments': assignments,
        'warning_cutoff': warning_cutoff,
        'due_soon_cutoff': due_soon_cutoff,
        'now': now,
        # timetable context
        'day_columns': day_columns,
        'today_entries': today_entries,
        'today_date': today,
        'week_num': week_num,
        'max_week': max_week,
        'current_week': current_week,
    })
