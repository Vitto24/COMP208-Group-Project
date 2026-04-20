from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST
from modules.models import Module, ModuleCourse
from grades.models import Grade, Assignment, Submission
from accounts.models import UserProfile # allows access to course info for year weights


def _fmt_int(n):
    # drop trailing .0 so 210.0 displays as 210 in the credits boxes
    return int(n) if n == int(n) else round(n, 1)


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

    submitted_ids = set(
        Submission.objects.filter(student=request.user).values_list('assignment_id', flat=True)
    )
    today = timezone.now().date()

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

            submitted = assign.id in submitted_ids
            if grade_record and grade_record.status == 'graded' and score is not None:
                status = 'graded'
            elif submitted or (grade_record and grade_record.status == 'submitted'):
                status = 'submitted'
            elif assign.due_date and assign.due_date < today:
                status = 'missing'
            else:
                status = 'upcoming'

            assignment_data.append({
                'assignment': assign,
                'score': score,
                'status': status,
            })

        # per-assignment counters so the summary boxes can show "5 of 10 Graded"
        graded_count = sum(1 for a in assignment_data if a['status'] == 'graded')
        total_count = len(assignment_data)
        fully_graded = total_count > 0 and graded_count == total_count

        # weighted sum of graded assignment scores for this module
        graded_weighted_sum = 0
        graded_weight_total = 0
        for a in assignment_data:
            if a['status'] == 'graded' and a['score'] is not None:
                w = float(a['assignment'].weight)
                graded_weighted_sum += float(a['score']) * w
                graded_weight_total += w

        mod_data = {
            'module': module,
            'grades': assignment_data,
            'overall_grade': round(total_weighted_mark, 1),
            'graded_count': graded_count,
            'total_count': total_count,
            'fully_graded': fully_graded,
            'graded_weighted_sum': graded_weighted_sum,
            'graded_weight_total': graded_weight_total,
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
        # Credits Completed: only count credits from modules where every assignment
        # has been graded (partially-graded modules don't earn their credits yet)
        for year_block in grouped_data:
            for sem_block in year_block['semesters']:
                for mod_item in sem_block['modules']:
                    c = float(mod_item['module'].credits)
                    total_degree_credits += c
                    if mod_item['fully_graded']:
                        total_degree_graded += c

        total_credits_str = f"{_fmt_int(total_degree_graded)}/{_fmt_int(total_degree_credits)}"

        # Most recent year: assignment-level counts + credit-weighted average
        recent_year = grouped_data[0]
        year_graded_assignments = 0
        year_total_assignments = 0
        year_weighted_sum = 0
        year_weight_total = 0

        for sem in recent_year['semesters']:
            for mod in sem['modules']:
                credits = float(mod['module'].credits)
                year_graded_assignments += mod['graded_count']
                year_total_assignments += mod['total_count']
                # weight graded-assignment marks by module credits so big modules matter more
                year_weighted_sum += mod['graded_weighted_sum'] * credits
                year_weight_total += mod['graded_weight_total'] * credits

        if year_weight_total > 0:
            current_year_avg = round(year_weighted_sum / year_weight_total, 1)
        year_subtitle = f"{year_graded_assignments} of {year_total_assignments} Graded"

        # Most recent semester: same pattern, scoped to first semester of recent year
        if recent_year['semesters']:
            recent_sem = recent_year['semesters'][0]
            sem_graded_assignments = 0
            sem_total_assignments = 0
            sem_weighted_sum = 0
            sem_weight_total = 0

            for mod in recent_sem['modules']:
                credits = float(mod['module'].credits)
                sem_graded_assignments += mod['graded_count']
                sem_total_assignments += mod['total_count']
                sem_weighted_sum += mod['graded_weighted_sum'] * credits
                sem_weight_total += mod['graded_weight_total'] * credits

            if sem_weight_total > 0:
                current_sem_avg = round(sem_weighted_sum / sem_weight_total, 1)

            sem_subtitle = f"{sem_graded_assignments} of {sem_total_assignments} Graded"

            sem_fully_graded_credits = sum(
                float(m['module'].credits) for m in recent_sem['modules'] if m['fully_graded']
            )
            sem_total_credits = sum(float(m['module'].credits) for m in recent_sem['modules'])
            credits_subtitle = (
                f"Semester {recent_sem['semester']}: "
                f"{_fmt_int(sem_fully_graded_credits)}/{_fmt_int(sem_total_credits)}"
            )

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


@login_required
@require_POST
def submit_assignment(request, assignment_id):
    assignment = get_object_or_404(Assignment, pk=assignment_id)

    # only let enrolled students submit
    if not assignment.module.students.filter(pk=request.user.pk).exists():
        messages.error(request, "You're not enrolled in that module.")
        return redirect('modules:module_detail', code=assignment.module.code)

    _, created = Submission.objects.get_or_create(
        student=request.user,
        assignment=assignment,
    )

    # also flip the Grade row so the status pill picks it up
    grade, _ = Grade.objects.get_or_create(
        student=request.user, assignment=assignment,
        defaults={'status': 'submitted'},
    )
    if grade.status == 'not_submitted':
        grade.status = 'submitted'
        grade.save()

    if created:
        messages.success(
            request,
            f"✅ '{assignment.title}' submitted. Your mark will appear here once the lecturer releases it.",
        )
    else:
        messages.info(request, f"Already submitted '{assignment.title}'.")

    return redirect('modules:module_detail', code=assignment.module.code)


@login_required
@require_POST
def mark_assignment(request, assignment_id):
    # demo-only: lets a staff user release a grade for themselves from the
    # module detail page, without going through /admin/. Real grading still
    # happens through the admin for other students.
    if not request.user.is_staff:
        messages.error(request, "You don't have permission to grade assignments.")
        return redirect('/')

    assignment = get_object_or_404(Assignment, pk=assignment_id)

    try:
        score = float(request.POST.get('score', '').strip())
    except ValueError:
        messages.error(request, 'Please enter a valid score.')
        return redirect('modules:module_detail', code=assignment.module.code)

    if score < 0 or score > 100:
        messages.error(request, 'Score must be between 0 and 100.')
        return redirect('modules:module_detail', code=assignment.module.code)

    # also record the submission so the audit trail matches the student-submit path
    Submission.objects.get_or_create(student=request.user, assignment=assignment)

    grade, _ = Grade.objects.get_or_create(
        student=request.user, assignment=assignment,
        defaults={'score': score, 'status': 'graded'},
    )
    grade.score = score
    grade.status = 'graded'
    grade.save()

    messages.success(request, f"Released a grade of {score:g}% for '{assignment.title}'.")
    return redirect('modules:module_detail', code=assignment.module.code)