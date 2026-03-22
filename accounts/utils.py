import random
from modules.models import Module, ModuleCourse

# each semester should total this many credits
CREDITS_PER_SEMESTER = 60


def _fill_semester(user, course_links, semester):
    """Enrol compulsory modules + random optionals to fill 60cr for one semester."""
    compulsory = []
    optional = []

    for link in course_links:
        if link.module.semester != semester:
            continue
        if link.is_compulsory:
            compulsory.append(link.module)
        else:
            optional.append(link.module)

    # always enrol compulsory modules
    compulsory_credits = 0
    for mod in compulsory:
        mod.students.add(user)
        compulsory_credits += mod.credits

    # fill remaining credits with random optional modules
    remaining = CREDITS_PER_SEMESTER - compulsory_credits
    if remaining <= 0:
        return

    # shuffle within each credit group for randomness, but pick
    # larger modules first so we don't end up with gaps we can't fill
    credit_groups = {}
    for mod in optional:
        cr = float(mod.credits)
        if cr not in credit_groups:
            credit_groups[cr] = []
        credit_groups[cr].append(mod)

    for group in credit_groups.values():
        random.shuffle(group)

    # sort by credits descending (pick 15cr before 7.5cr)
    sorted_optional = []
    for cr in sorted(credit_groups.keys(), reverse=True):
        sorted_optional.extend(credit_groups[cr])

    for mod in sorted_optional:
        if mod.credits <= remaining:
            mod.students.add(user)
            remaining -= mod.credits
        if remaining <= 0:
            break


def auto_enrol_compulsory(user):
    """Enrol a user in compulsory modules + random optionals for all years.

    Fills 60 credits per semester for every year up to and including the
    student's current year of study. Clears existing course-linked modules
    first so changes to course or year are always reflected.
    """
    try:
        profile = user.userprofile
    except Exception:
        return

    # remove user from all modules linked to any course (clean slate)
    course_modules = Module.objects.filter(module_courses__isnull=False).distinct()
    for mod in course_modules:
        mod.students.remove(user)

    if not profile.course:
        return

    # get all distinct years for this course
    all_years = (
        ModuleCourse.objects.filter(course=profile.course)
        .values_list('year', flat=True)
        .distinct()
    )

    for year_str in all_years:
        # skip non-numeric years (FP, S1, S2)
        if not year_str.isdigit():
            continue
        year_num = int(year_str)

        # don't enrol in years above the student's current year
        if year_num > profile.year_of_study:
            continue

        # get module links for this year
        course_links = ModuleCourse.objects.filter(
            course=profile.course,
            year=year_str,
        ).select_related('module')

        for semester in [1, 2]:
            _fill_semester(user, course_links, semester)


def update_module_selection(user, selected_codes):
    """Update a student's optional module selection for their current year.

    Compulsory modules are always kept. Optional modules are added/removed
    based on the selected_codes list. Previous years are not modified.
    Returns (success, error_message).
    """
    try:
        profile = user.userprofile
    except Exception:
        return False, 'No user profile found.'

    if not profile.course:
        return False, 'No course selected.'

    year_str = str(profile.year_of_study)

    # only update modules for the current year (previous years are read-only)
    course_links = ModuleCourse.objects.filter(
        course=profile.course,
        year=year_str,
    ).select_related('module')

    # remove user from current year's modules
    for link in course_links:
        link.module.students.remove(user)

    # always add compulsory modules back
    for link in course_links:
        if link.is_compulsory:
            link.module.students.add(user)

    # add selected optional modules
    for link in course_links:
        if not link.is_compulsory and link.module.code in selected_codes:
            link.module.students.add(user)

    # validate credits per semester for current year only
    for semester in [1, 2]:
        enrolled = Module.objects.filter(
            students=user,
            semester=semester,
            module_courses__course=profile.course,
            module_courses__year=year_str,
        ).distinct()

        total_credits = sum(m.credits for m in enrolled)

        # check if this semester even has modules for this year
        semester_links = [l for l in course_links if l.module.semester == semester]
        if semester_links and total_credits != CREDITS_PER_SEMESTER:
            return False, f'Year {year_str} Semester {semester} has {total_credits} credits — must be {CREDITS_PER_SEMESTER}.'

    return True, None
