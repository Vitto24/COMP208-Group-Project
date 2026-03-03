from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from modules.models import Module
from grades.models import Grade


@login_required
def grades(request):
    modules = Module.objects.filter(students=request.user)

    # list of dictionaries to hold the module grades
    module_data = []
    for module in modules:
        # Grab only grades for the current user in that module
        module_grades = Grade.objects.filter(
            assignment__module=module,
            student=request.user,
        )

        total_weighted_mark = 0

        for g in module_grades:
            # calculate the weighted mark for each grade, and add it to the total
            score = g.score or 0
            weight = (g.assignment.weight / 100) or 0

            total_weighted_mark += (score * weight)

        module_data.append({
            'module': module,
            'grades': module_grades,
            'overall_grade': round(total_weighted_mark, 1)
        })

    return render(request, 'grades/grades.html', {'module_data': module_data})
