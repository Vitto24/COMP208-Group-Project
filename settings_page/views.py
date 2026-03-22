from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from modules.models import Course, Module, ModuleCourse
from accounts.models import UserProfile
from accounts.utils import auto_enrol_compulsory, update_module_selection, CREDITS_PER_SEMESTER


@login_required
def settings_view(request):
    # Make sure the user has a profile
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()

        # Make sure required fields aren't empty
        if not first_name or not last_name or not email:
            messages.error(request, 'First name, last name, and email are required.')
            return redirect('settings_page:settings')

        # Update basic user info
        request.user.first_name = first_name
        request.user.last_name = last_name
        request.user.email = email
        request.user.save()

        # Update profile fields
        course_id = request.POST.get('course', '')
        if course_id:
            try:
                profile.course = Course.objects.get(id=course_id)
            except Course.DoesNotExist:
                profile.course = None
        else:
            profile.course = None

        year = request.POST.get('year_of_study', '1')
        try:
            profile.year_of_study = int(year)
        except ValueError:
            profile.year_of_study = 1

        profile.save()

        # Re-run auto-enrolment with the updated course/year
        auto_enrol_compulsory(request.user)

        messages.success(request, 'Settings saved.')
        return redirect('settings_page:settings')

    courses = Course.objects.all().order_by('name')

    # build module selection data for ALL years
    year_data = _build_year_data(request.user, profile)

    context = {
        'profile': profile,
        'courses': courses,
        'year_choices': range(1, 5),
        'year_data': year_data,
    }
    return render(request, 'settings_page/settings.html', context)


def _build_year_data(user, profile):
    """Build the year → semester → module structure for the template."""
    if not profile.course:
        return []

    enrolled_codes = set(
        Module.objects.filter(students=user).values_list('code', flat=True)
    )

    # get all distinct numeric years for this course (up to current year)
    all_years = (
        ModuleCourse.objects.filter(course=profile.course)
        .values_list('year', flat=True)
        .distinct()
    )

    numeric_years = []
    for y in all_years:
        if y.isdigit() and int(y) <= profile.year_of_study:
            numeric_years.append(int(y))

    # sort descending (current year first)
    numeric_years.sort(reverse=True)

    year_data = []
    for year_num in numeric_years:
        year_str = str(year_num)
        is_current = (year_num == profile.year_of_study)

        links = ModuleCourse.objects.filter(
            course=profile.course,
            year=year_str,
        ).select_related('module').order_by('module__code')

        semesters = []
        # semesters in descending order (sem 2 first, like grades page)
        for semester in [2, 1]:
            compulsory = []
            optional = []

            for link in links:
                if link.module.semester != semester:
                    continue
                mod_info = {
                    'code': link.module.code,
                    'name': link.module.name,
                    'credits': link.module.credits,
                    'is_compulsory': link.is_compulsory,
                    'enrolled': link.module.code in enrolled_codes,
                }
                if link.is_compulsory:
                    compulsory.append(mod_info)
                else:
                    optional.append(mod_info)

            # only include semesters that have modules
            if not compulsory and not optional:
                continue

            compulsory_credits = sum(m['credits'] for m in compulsory)
            enrolled_optional_credits = sum(
                m['credits'] for m in optional if m['enrolled']
            )
            total_credits = compulsory_credits + enrolled_optional_credits

            semesters.append({
                'semester': semester,
                'compulsory': compulsory,
                'optional': optional,
                'total_credits': total_credits,
                'target_credits': CREDITS_PER_SEMESTER,
            })

        if semesters:
            year_data.append({
                'year': year_num,
                'is_current': is_current,
                'semesters': semesters,
            })

    return year_data


@login_required
def update_modules(request):
    """Handle the module selection form submission."""
    if request.method != 'POST':
        return redirect('settings_page:settings')

    # get all selected module codes from the checkboxes
    selected_codes = request.POST.getlist('modules')

    success, error = update_module_selection(request.user, selected_codes)
    if success:
        messages.success(request, 'Module selection saved.')
    else:
        messages.error(request, error)

    return redirect('settings_page:settings')
