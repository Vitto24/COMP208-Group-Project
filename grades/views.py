from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone
from modules.models import Module
from grades.models import Grade, Assignment 
from accounts.models import UserProfile # allows access to course info for year weights

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

    # --- Top section maths ---
    current_sem_avg = 0
    current_year_avg = 0
    degree_projection = 0
    credits_str = "0/0"

    # only do if has any data to work with
    if grouped_data:
        recent_year = grouped_data[0] # Newest year (e.g., Year 2)
        year_total_weighted = 0
        year_total_credits = 0

        # Average grade for current year
        for sem in recent_year['semesters']:
            for mod in sem['modules']:
                credits = float(mod['module'].credits)
                grade = mod['overall_grade']
                
                if grade > 0: # Only count if graded
                    year_total_weighted += (grade * credits)
                    year_total_credits += credits
        
        if year_total_credits > 0:
            current_year_avg = round(year_total_weighted / year_total_credits, 1)

        # Average grade for semester
        if recent_year['semesters']:
            recent_sem = recent_year['semesters'][0]
            sem_total_weighted = 0
            sem_graded_credits = 0
            sem_total_credits = 0

            for mod in recent_sem['modules']:
                credits = float(mod['module'].credits)
                grade = mod['overall_grade']
                sem_total_credits += credits
                
                if grade > 0:
                    sem_total_weighted += (grade * credits)
                    sem_graded_credits += credits

            if sem_graded_credits > 0:
                current_sem_avg = round(sem_total_weighted / sem_graded_credits, 1)
            
            # Format credits like "15/60"
            credits_str = f"{int(sem_graded_credits)}/{int(sem_total_credits)}"

        # Degree projection - just year average for now
        degree_projection = current_year_avg

    
    weights = {'y1': 0, 'y2': 30, 'y3': 70} 
    if hasattr(request.user, 'userprofile') and request.user.userprofile.course:
        course = request.user.userprofile.course
        weights['y1'] = course.year_1_weight
        weights['y2'] = course.year_2_weight
        weights['y3'] = course.year_3_weight

    return render(request, 'grades/grades.html', {
        'grouped_data': grouped_data,
        'today': timezone.now().date(),
        'current_sem_avg': current_sem_avg,
        'current_year_avg': current_year_avg,
        'degree_projection': degree_projection,
        'credits_completed': credits_str,
        'weights': weights, 
    })