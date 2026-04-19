from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from .models import Module, Week
from modules.models import ModuleCourse
from grades.models import Assignment, Grade, Submission
from timetable.utils import get_current_semester, get_current_week


@login_required
def module_list(request):
    current_sem = get_current_semester()
    profile = getattr(request.user, 'userprofile', None)
    current_year = profile.year_of_study if profile else 1
    other_sem = 1 if current_sem == 2 else 2

    enrolled = list(
        Module.objects.filter(students=request.user).order_by('code')
    )

    # map each enrolled module to its year-of-course via the ModuleCourse table
    module_year = {}
    if profile and profile.course:
        links = ModuleCourse.objects.filter(
            course=profile.course,
            module_id__in=[m.id for m in enrolled],
        ).values_list('module_id', 'year')
        for mid, year in links:
            if year.isdigit():
                module_year[mid] = int(year)

    current_modules = []
    earlier_this_year = []
    past_buckets = {}  # year_num -> {1: [...], 2: [...]}

    for module in enrolled:
        y = module_year.get(module.id)
        if y is None:
            continue

        if y == current_year and module.semester == current_sem:
            current_modules.append(module)
        elif y == current_year:
            earlier_this_year.append(module)
        elif y < current_year:
            bucket = past_buckets.setdefault(y, {1: [], 2: []})
            bucket[module.semester].append(module)

    past_years = []
    for y in sorted(past_buckets.keys(), reverse=True):
        semesters = []
        for sem in (2, 1):
            mods = past_buckets[y][sem]
            if mods:
                semesters.append({'semester': sem, 'modules': mods})
        if semesters:
            past_years.append({'year': y, 'semesters': semesters})

    return render(request, 'modules/module_list.html', {
        'current_modules': current_modules,
        'earlier_this_year': earlier_this_year,
        'past_years': past_years,
        'current_year': current_year,
        'current_sem': current_sem,
        'other_sem': other_sem,
    })


@login_required
def module_detail(request, code):
    """
    Display detailed information for a single module.
    """
    module = get_object_or_404(Module, code=code)

    if not module.students.filter(pk=request.user.pk).exists():
        raise Http404

    assignments = list(Assignment.objects.filter(module=module).order_by('due_date'))

    # pull this user's grade + submission state in one pass
    grades_by_aid = {
        g.assignment_id: g
        for g in Grade.objects.filter(student=request.user, assignment__module=module)
    }
    submitted_aids = set(
        Submission.objects.filter(
            student=request.user, assignment__module=module,
        ).values_list('assignment_id', flat=True)
    )

    today = timezone.now().date()
    rows = []
    for a in assignments:
        grade = grades_by_aid.get(a.id)
        submitted = a.id in submitted_aids

        if grade and grade.status == 'graded' and grade.score is not None:
            status = 'graded'
        elif submitted or (grade and grade.status == 'submitted'):
            status = 'submitted'
        elif a.due_date and a.due_date < today:
            status = 'missing'
        else:
            status = 'upcoming'

        rows.append({
            'assignment': a,
            'status': status,
            'score': grade.score if grade else None,
            'submitted': submitted or status == 'submitted',
        })

    weeks = Week.objects.filter(module=module).prefetch_related('materials')
    current_week = get_current_week(module.semester)

    return render(request, 'modules/module_detail.html', {
        'module': module,
        'assignments': assignments,
        'assignment_rows': rows,
        'weeks': weeks,
        'current_week': current_week,
    })
