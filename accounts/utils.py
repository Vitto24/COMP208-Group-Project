import datetime
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


def enrol_compulsory_only(user):
    """Enrol a user in ONLY compulsory modules for all years.

    Used during registration so the user can then manually pick their
    optional modules on the module selection page.
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

    all_years = (
        ModuleCourse.objects.filter(course=profile.course)
        .values_list('year', flat=True)
        .distinct()
    )

    for year_str in all_years:
        if not year_str.isdigit():
            continue
        if int(year_str) > profile.year_of_study:
            continue

        links = ModuleCourse.objects.filter(
            course=profile.course,
            year=year_str,
            is_compulsory=True,
        ).select_related('module')

        for link in links:
            link.module.students.add(user)


def randomise_optional_modules(user):
    """Fill remaining credits with random optionals for all years.

    Keeps existing compulsory enrolments and adds random optionals
    to reach 60 credits per semester.
    """
    try:
        profile = user.userprofile
    except Exception:
        return

    if not profile.course:
        return

    all_years = (
        ModuleCourse.objects.filter(course=profile.course)
        .values_list('year', flat=True)
        .distinct()
    )

    for year_str in all_years:
        if not year_str.isdigit():
            continue
        if int(year_str) > profile.year_of_study:
            continue

        course_links = ModuleCourse.objects.filter(
            course=profile.course,
            year=year_str,
        ).select_related('module')

        for semester in [1, 2]:
            # check how many credits are already enrolled
            enrolled = Module.objects.filter(
                students=user,
                semester=semester,
                module_courses__course=profile.course,
                module_courses__year=year_str,
            ).distinct()
            current_credits = sum(m.credits for m in enrolled)

            if current_credits >= CREDITS_PER_SEMESTER:
                continue

            # get optional modules not yet enrolled
            optional = []
            for link in course_links:
                if link.module.semester != semester:
                    continue
                if link.is_compulsory:
                    continue
                if not link.module.students.filter(pk=user.pk).exists():
                    optional.append(link.module)

            remaining = CREDITS_PER_SEMESTER - current_credits

            # shuffle within credit groups, pick largest first
            credit_groups = {}
            for mod in optional:
                cr = float(mod.credits)
                if cr not in credit_groups:
                    credit_groups[cr] = []
                credit_groups[cr].append(mod)

            for group in credit_groups.values():
                random.shuffle(group)

            sorted_optional = []
            for cr in sorted(credit_groups.keys(), reverse=True):
                sorted_optional.extend(credit_groups[cr])

            for mod in sorted_optional:
                if mod.credits <= remaining:
                    mod.students.add(user)
                    remaining -= mod.credits
                if remaining <= 0:
                    break


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


def finalise_registration(user, selected_codes):
    """Apply module selection across every year up to the student's current year.

    Used only during the initial sign-up flow so a Y2+ student can backfill
    their earlier years before landing on the dashboard. Returns (success, error).
    """
    try:
        profile = user.userprofile
    except Exception:
        return False, 'No user profile found.'

    if not profile.course:
        return False, 'No course selected.'

    selected_set = set(selected_codes)

    # wipe course-linked enrolments so we rebuild from scratch
    course_modules = Module.objects.filter(module_courses__course=profile.course).distinct()
    for mod in course_modules:
        mod.students.remove(user)

    years = list(range(1, profile.year_of_study + 1))

    for year_num in years:
        year_str = str(year_num)
        links = ModuleCourse.objects.filter(
            course=profile.course, year=year_str,
        ).select_related('module')

        for link in links:
            if link.is_compulsory:
                link.module.students.add(user)
            elif link.module.code in selected_set:
                link.module.students.add(user)

        # validate each semester for every year
        for semester in [1, 2]:
            enrolled = Module.objects.filter(
                students=user,
                semester=semester,
                module_courses__course=profile.course,
                module_courses__year=year_str,
            ).distinct()

            total_credits = sum(m.credits for m in enrolled)

            semester_links = [l for l in links if l.module.semester == semester]
            if semester_links and total_credits != CREDITS_PER_SEMESTER:
                return False, (
                    f'Year {year_str} Semester {semester} has {total_credits} credits '
                    f'— must be {CREDITS_PER_SEMESTER}.'
                )

    return True, None


def generate_timetable_for_user(user):
    """Give a freshly registered student timetable entries for every module they're in.

    For modules that already have a schedule (another student is enrolled), copy
    theirs so everyone on the module sees the same classes. If the module has no
    entries yet, fabricate a small 3-event schedule so the timetable isn't blank.
    """
    from timetable.models import TimetableEntry

    days = ['MON', 'TUE', 'WED', 'THU', 'FRI']
    rooms = [
        'Central Teaching Hub - LT1',
        'Central Teaching Hub - LT2',
        'Ashton Lecture Theatre',
        'Rendall Building - LT1',
        'George Holt Building - Room 101',
    ]

    for module in Module.objects.filter(students=user):
        # skip modules the user already has entries for
        if TimetableEntry.objects.filter(student=user, module=module).exists():
            continue

        # copy an existing student's schedule if one exists
        reference = (
            TimetableEntry.objects
            .filter(module=module)
            .exclude(student=user)
            .first()
        )
        if reference:
            ref_entries = TimetableEntry.objects.filter(
                module=module, student=reference.student,
            )
            for ref in ref_entries:
                TimetableEntry.objects.create(
                    student=user, module=module,
                    day=ref.day, start_time=ref.start_time, end_time=ref.end_time,
                    room=ref.room, event_type=ref.event_type,
                    semester=ref.semester, weeks=ref.weeks,
                )
            continue

        # no reference — fabricate a small schedule
        # deterministic per module code so re-running doesn't shuffle slots
        h = sum(ord(c) for c in module.code)
        events = [
            ('Lecture', days[h % 5], 9 + (h % 7)),
            ('Lecture', days[(h + 2) % 5], 10 + ((h + 3) % 6)),
            ('Tutorial', days[(h + 4) % 5], 13 + ((h + 5) % 4)),
        ]
        for event_type, day, hour in events:
            TimetableEntry.objects.create(
                student=user, module=module,
                day=day,
                start_time=datetime.time(hour, 0),
                end_time=datetime.time(hour + 1, 0),
                room=rooms[h % len(rooms)],
                event_type=event_type,
                semester=module.semester,
                weeks='1-12',
            )


def randomise_prior_year_grades(user):
    """Fill sample grades for every assignment the student took in past years.

    Only touches years below the student's current year. Uses the same gaussian
    distribution as generate_sample_data so the numbers look realistic.
    """
    from grades.models import Assignment, Grade  # local import to avoid a cycle

    try:
        profile = user.userprofile
    except Exception:
        return

    if not profile.course or profile.year_of_study <= 1:
        return

    prior_year_strs = [str(y) for y in range(1, profile.year_of_study)]

    prior_modules = Module.objects.filter(
        students=user,
        module_courses__course=profile.course,
        module_courses__year__in=prior_year_strs,
    ).distinct()

    today = datetime.date.today()
    for module in prior_modules:
        for assignment in Assignment.objects.filter(module=module):
            # don't overwrite existing marks
            if Grade.objects.filter(student=user, assignment=assignment).exists():
                continue

            # only fake-mark past-dated assignments, leave future ones alone
            if assignment.due_date and assignment.due_date > today:
                continue

            score = round(max(30, min(95, random.gauss(65, 12))), 1)
            Grade.objects.create(
                student=user, assignment=assignment,
                score=score, status='graded',
            )
