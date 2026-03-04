from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone
from modules.models import Module
from grades.models import Grade, Assignment # <-- Notice we imported Assignment here now!

@login_required
def grades(request):
    modules = Module.objects.filter(students=request.user).order_by('-year', 'semester')
    grouped_dict = {}

    for module in modules:
        # Fetch ALL assignments for the module, not just graded ones
        assignments = Assignment.objects.filter(module=module).order_by('due_date')

        assignment_data = []
        total_weighted_mark = 0

        for assign in assignments:
            # Try to find a grade specifically for this student and this assignment
            grade_record = Grade.objects.filter(assignment=assign, student=request.user).first()

            score = None
            if grade_record and grade_record.score:
                score = grade_record.score
                weight = assign.weight / 100
                total_weighted_mark += float(score) * float(weight)

            assignment_data.append({
                'assignment': assign,
                'score': score,
            })

        mod_data = {
            'module': module,
            'grades': assignment_data, 
            'overall_grade': round(total_weighted_mark, 1)
        }

        # Group it by year and semester
        y = module.year
        s = module.semester

        if y not in grouped_dict:
            grouped_dict[y] = {}
        if s not in grouped_dict[y]:
            grouped_dict[y][s] = []
            
        grouped_dict[y][s].append(mod_data)

    # Convert the dictionary into a list for the template
    grouped_data = []
    for year, semesters in grouped_dict.items():
        sem_list = []
        for sem, mods in semesters.items():
            sem_list.append({'semester': sem, 'modules': mods})
        sem_list.sort(key=lambda x: x['semester'], reverse=True)
        grouped_data.append({'year': year, 'semesters': sem_list})

    grouped_data.sort(key=lambda x: x['year'], reverse=True)

    return render(request, 'grades/grades.html', {
        'grouped_data': grouped_data,
        'today': timezone.now().date()
    })