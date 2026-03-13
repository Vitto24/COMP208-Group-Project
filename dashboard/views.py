from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from modules.models import Module
from grades.models import Assignment
from django.utils import timezone
from datetime import timedelta
from timetable.utils import get_current_semester

DEADLINE_WARNING_DAYS = 3
DUE_SOON_DAYS = 7


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
    return render(request, 'dashboard/dashboard.html', {
        'modules': modules,
        'assignments': assignments,
        'warning_cutoff': warning_cutoff,
        'due_soon_cutoff': due_soon_cutoff,
        'now': now,
    })
