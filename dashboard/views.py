from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from modules.models import Module
from grades.models import Assignment
from django.utils import timezone
from datetime import timedelta

DEADLINE_WARNING_DAYS = 3
DUE_SOON_DAYS = 7


@login_required
def dashboard(request):
    modules = Module.objects.filter(students=request.user)

    now = timezone.now()
    warning_cutoff = now + timedelta(days=DEADLINE_WARNING_DAYS)

    assignments = Assignment.objects.filter(
        module__students=request.user,
        due_date__gte=now,
    ).order_by('due_date')
    return render(request, 'dashboard/dashboard.html', {
        'modules': modules,
        'assignments': assignments,
        'warning_cutoff': warning_cutoff,
        'now': now,
    })
