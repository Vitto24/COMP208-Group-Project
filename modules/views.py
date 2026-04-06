from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from .models import Module, Week
from grades.models import Assignment


@login_required
def module_list(request):
    """
    Display a list of all modules.
    """
    modules = Module.objects.filter(students=request.user)

    # split into current academic year and previous
    current_modules = modules.filter(academic_year='2025/26')
    previous_modules = modules.exclude(academic_year='2025/26')

    return render(request, 'modules/module_list.html', {
        'current_modules': current_modules,
        'previous_modules': previous_modules
    })


@login_required
def module_detail(request, code):
    """
    Display detailed information for a single module.
    """
    module = get_object_or_404(Module, code=code)

    if not module.students.filter(pk=request.user.pk).exists():
        raise Http404

    assignments = Assignment.objects.filter(module=module)

    weeks = Week.objects.filter(module=module).prefetch_related('materials')

    return render(request, 'modules/module_detail.html', {
        'module': module,
        'assignments': assignments,
        'weeks': weeks
    })
