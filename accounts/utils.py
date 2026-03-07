from modules.models import Module, ModuleCourse


def auto_enrol_compulsory(user):
    """Enrol a user in all compulsory modules for their course and year.

    Clears any existing course-linked modules first, then re-enrols
    the correct ones so changes to course or year are always reflected.
    """
    try:
        profile = user.userprofile
    except Exception:
        return

    # Remove user from all modules linked to any course (clean slate)
    course_modules = Module.objects.filter(module_courses__isnull=False).distinct()
    for mod in course_modules:
        mod.students.remove(user)

    if not profile.course:
        return

    # Get all modules for this course and year (compulsory + optional)
    year_str = str(profile.year_of_study)
    course_links = ModuleCourse.objects.filter(
        course=profile.course,
        year=year_str,
    ).select_related('module')

    for link in course_links:
        # add() is a no-op if the user is already enrolled
        link.module.students.add(user)
