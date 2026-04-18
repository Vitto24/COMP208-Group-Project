from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone
from modules.models import Module, ModuleCourse
from grades.models import Grade, Assignment
from accounts.models import UserProfile # allows access to course info for year weights

@login_required
def grades(request):
    # get the student's year-of-course for each module (e.g. COMP108 is Year 1 on CS BSc)
    course = request.user.userprofile.course if hasattr(request.user, 'userprofile') else None
    module_year_map = {}
    if course:
        for mc in ModuleCourse.objects.filter(course=course):
            module_year_map[mc.module_id] = mc.year

    modules = Module.objects.filter(students=request.user).order_by('semester')
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

        # Group it by the student's year-of-course and semester
        y = module_year_map.get(module.id, str(module.year))
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
    
    # Trackers for the big total progress box
    total_degree_graded = 0
    total_degree_credits = 0
    
    # Subtitles for the UI
    sem_subtitle = "0 of 0 Graded"
    year_subtitle = "0 of 0 Graded"
    projection_subtitle = "N/A"
    credits_subtitle = "No Data"
    total_credits_str = "0/0"

    # only do if has any data to work with
    if grouped_data:
        for year_block in grouped_data:
            for sem_block in year_block['semesters']:
                for mod_item in sem_block['modules']:
                    c = float(mod_item['module'].credits)
                    total_degree_credits += c
                    if mod_item['overall_grade'] > 0:
                        total_degree_graded += c
        
        # Big number for the far right box (e.g., 181.5/360)
        total_credits_str = f"{total_degree_graded}/{total_degree_credits}"

        # Most recent year average and counts
        recent_year = grouped_data[0] 
        year_total_weighted = 0
        year_graded_credits = 0
        year_total_count = 0
        year_graded_count = 0

        for sem in recent_year['semesters']:
            for mod in sem['modules']:
                credits = float(mod['module'].credits)
                grade = mod['overall_grade']
                year_total_count += 1
                
                if grade > 0: # Only count if graded
                    year_total_weighted += (grade * credits)
                    year_graded_credits += credits
                    year_graded_count += 1
        
        if year_graded_credits > 0:
            current_year_avg = round(year_total_weighted / year_graded_credits, 1)
        if year_total_count > 0:
            year_subtitle = f"{year_graded_count} of {year_total_count} Graded"

        # Most recent semester average and counts
        if recent_year['semesters']:
            recent_sem = recent_year['semesters'][0]
            sem_total_weighted = 0
            sem_graded_credits = 0
            sem_total_credits = 0
            sem_graded_count = 0

            for mod in recent_sem['modules']:
                credits = float(mod['module'].credits)
                grade = mod['overall_grade']
                sem_total_credits += credits
                
                if grade > 0:
                    sem_total_weighted += (grade * credits)
                    sem_graded_credits += credits
                    sem_graded_count += 1

            if sem_graded_credits > 0:
                current_sem_avg = round(sem_total_weighted / sem_graded_credits, 1)
            
            # Subtitles for the semester stats
            sem_subtitle = f"{sem_graded_count} of {len(recent_sem['modules'])} Graded"
            credits_subtitle = f"Semester {recent_sem['semester']}: {int(sem_graded_credits)}/{int(sem_total_credits)}"

    # Fetch course weightings for the current student (needed for projection)
    weights = {'y1': 0, 'y2': 30, 'y3': 70, 'y4': 0, 'y5': 0}
    if hasattr(request.user, 'userprofile') and request.user.userprofile.course:
        c = request.user.userprofile.course
        weights['y1'] = c.year_1_weight
        weights['y2'] = c.year_2_weight
        weights['y3'] = c.year_3_weight
        weights['y4'] = c.year_4_weight
        weights['y5'] = c.year_5_weight

    if grouped_data:
        # Degree projection = weighted average across years with data, renormalised
        # so a Year 1 student only sees a projection once they have weighted years
        year_averages = {}
        for year_block in grouped_data:
            total_w = 0
            total_c = 0
            for sem_block in year_block['semesters']:
                for mod_item in sem_block['modules']:
                    g = mod_item['overall_grade']
                    cr = float(mod_item['module'].credits)
                    if g > 0:
                        total_w += g * cr
                        total_c += cr
            if total_c > 0:
                year_averages[str(year_block['year'])] = total_w / total_c

        weighted_sum = 0
        weight_used = 0
        for y_str, avg in year_averages.items():
            w = weights.get(f'y{y_str}', 0)
            weighted_sum += avg * w
            weight_used += w

        if weight_used > 0:
            degree_projection = round(weighted_sum / weight_used, 1)
            if degree_projection >= 70:
                projection_subtitle = "First Class (1st)"
            elif degree_projection >= 60:
                projection_subtitle = "Upper Second (2:1)"
            elif degree_projection >= 50:
                projection_subtitle = "Lower Second (2:2)"
            elif degree_projection >= 40:
                projection_subtitle = "Third Class (3rd)"
            else:
                projection_subtitle = "Pass/Fail"
        else:
            degree_projection = 0
            projection_subtitle = "Year 1 doesn't count"

    return render(request, 'grades/grades.html', {
        'grouped_data': grouped_data,
        'today': timezone.now().date(),
        'current_sem_avg': current_sem_avg,
        'current_year_avg': current_year_avg,
        'degree_projection': degree_projection,
        'credits_completed': total_credits_str, 
        'weights': weights, 
        'sem_subtitle': sem_subtitle,
        'year_subtitle': year_subtitle,
        'projection_subtitle': projection_subtitle,
        'credits_subtitle': credits_subtitle, 
    })