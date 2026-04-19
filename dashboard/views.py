from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from modules.models import Module
from grades.models import Assignment, Submission
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
PANEL_DAYS = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']
DAY_MAP = {0: 'MON', 1: 'TUE', 2: 'WED', 3: 'THU', 4: 'FRI', 5: 'SAT', 6: 'SUN'}


def _deadline_pill(days_left, submitted):
    # returns a (css class, label) pair used by both dashboard and timetable deadlines lists
    if submitted:
        return 'status-submitted', 'Submitted'
    if days_left <= 0:
        return 'status-missing', 'Today'
    if days_left == 1:
        return 'status-missing', 'Tomorrow'
    if days_left < 4:
        return 'status-missing', f'In {days_left} days'
    if days_left <= 14:
        return 'status-upcoming', f'In {days_left} days'
    return 'status-graded', f'In {days_left} days'


@login_required
def dashboard(request):
    semester = get_current_semester()

    # only show modules for the student's current year of study
    profile = getattr(request.user, 'userprofile', None)
    if not profile or not profile.course:
        today = datetime.date.today()
        return render(request, 'dashboard/dashboard.html', {
            'modules': [],
            'assignments': [],
            'deadline_rows': [],
            'day_columns': [],
            'today_entries': [],
            'today_date': today,
            'week_num': 1, 'max_week': 12, 'current_week': 1,
            'selected_day': 'MON', 'selected_day_date': None,
            'viewing_today': False, 'relative_label': '',
            'prev_day': None, 'prev_week': None,
            'next_day': None, 'next_week': None,
            'warning_cutoff': None, 'due_soon_cutoff': None,
            'now': timezone.now(),
        })
    year_str = str(profile.year_of_study)

    modules = Module.objects.filter(
        students=request.user,
        semester=semester,
        academic_year='2025/26',
        module_courses__course=profile.course,
        module_courses__year=year_str,
    ).distinct().order_by('code')

    now = timezone.now()
    warning_cutoff = now + timedelta(days=DEADLINE_WARNING_DAYS)
    due_soon_cutoff = now + timedelta(days=DUE_SOON_DAYS)

    assignments = Assignment.objects.filter(
        module__students=request.user,
        module__semester=semester,
        module__academic_year='2025/26',
        module__module_courses__course=profile.course,
        module__module_courses__year=year_str,
        due_date__gte=now,
    ).distinct().order_by('due_date')

    submitted_ids = set(
        Submission.objects.filter(student=request.user).values_list('assignment_id', flat=True)
    )

    today = now.date()
    deadline_rows = []
    for a in assignments:
        days_left = (a.due_date - today).days if a.due_date else 999
        pill_class, pill_label = _deadline_pill(days_left, a.id in submitted_ids)
        deadline_rows.append({
            'assignment': a,
            'pill_class': pill_class,
            'pill_label': pill_label,
        })

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

    # ── Timetable: fetch all entries for this semester, current year only ──
    all_entries = TimetableEntry.objects.filter(
        student=request.user,
        semester=semester,
        module__module_courses__course=profile.course,
        module__module_courses__year=year_str,
    ).select_related('module').distinct()

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

    # ── Day selector for the "Today" panel (same logic as timetable page) ─
    default_day = today_code if is_current_week else 'MON'
    selected_day = request.GET.get('day', default_day)
    if selected_day not in PANEL_DAYS:
        selected_day = default_day

    # figure out the date for that day (Sat/Sun offset from Monday)
    if selected_day in week_dates:
        selected_day_date = week_dates[selected_day]
    elif week_monday:
        offset = PANEL_DAYS.index(selected_day)
        selected_day_date = week_monday + datetime.timedelta(days=offset)
    else:
        selected_day_date = None

    viewing_today = (selected_day_date == today)

    # relative label text (Today / Tomorrow / in 3 days etc.)
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

    # prev/next day codes with week crossing (Sun ↔ next week's Mon)
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

    # events for the selected day (only Mon-Fri have any)
    today_entries = []
    current_time = datetime.datetime.now().time()

    selected_events = sorted(
        [e for e in week_entries if e.day == selected_day],
        key=lambda e: e.start_time,
    )
    for entry in selected_events:
        if viewing_today:
            if entry.end_time <= current_time:
                status = 'done'
            elif entry.start_time <= current_time:
                status = 'now'
            else:
                status = 'upcoming'
        else:
            status = ''
        today_entries.append({'entry': entry, 'status': status})

    return render(request, 'dashboard/dashboard.html', {
        'modules': modules,
        'assignments': assignments,
        'deadline_rows': deadline_rows,
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
        # day selector
        'selected_day': selected_day,
        'selected_day_date': selected_day_date,
        'viewing_today': viewing_today,
        'relative_label': relative_label,
        'prev_day': prev_day,
        'prev_week': prev_week,
        'next_day': next_day,
        'next_week': next_week,
    })
