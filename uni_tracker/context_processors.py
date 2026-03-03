from timetable.utils import get_current_semester, get_current_week


def semester_info(request):
    semester = get_current_semester()
    week = get_current_week(semester)
    return {
        'semester_info': f'Week {week} \u00b7 Semester {semester} (25/26)',
    }
