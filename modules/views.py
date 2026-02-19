from django.shortcuts import render, get_object_or_404
from .models import Module, Week
from grades.models import Assignment

def module_list(request):
    modules = Module.objects.all()
    return render(request, 'modules/module_list.html', {'modules': modules})

def module_detail(request, code):
    # Grab the specific module
    module = get_object_or_404(Module, code=code)
    # Grab all assignments for this module
    assignments = Assignment.objects.filter(module=module)
    # Grab the weeks and pre-fetch the materials so it doesn't lag out
    weeks = Week.objects.filter(module=module).prefetch_related('materials')
    
    return render(request, 'modules/module_detail.html', {
        'module': module,
        'assignments': assignments,
        'weeks': weeks
    })