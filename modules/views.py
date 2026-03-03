from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render, get_object_or_404
from .models import Module, Week
from grades.models import Assignment


@login_required
def module_list(request):
    """
    Display a list of all modules.
    """
    # Fetch only modules the current user is enrolled in
    modules = Module.objects.filter(students=request.user)

    # Render the module list page with the modules data
    return render(request, 'modules/module_list.html', {
        'modules': modules
    })


@login_required
def module_detail(request, code):
    """
    Display detailed information for a single module.
    """
    # Fetch the module or return 404 if it doesn't exist (e.g. if url is wrong)
    module = get_object_or_404(Module, code=code)

    # Check the user is enrolled in this module
    if not module.students.filter(pk=request.user.pk).exists():
        raise Http404

    # Fetch all assignments related to the module
    assignments = Assignment.objects.filter(module=module)

    # Fetch all weeks for this module and prefetch related materials
    weeks = Week.objects.filter(module=module).prefetch_related('materials')

    # Render the module detail page with all required data
    return render(request, 'modules/module_detail.html', {
        'module': module,
        'assignments': assignments,
        'weeks': weeks
    })
