from modules.models import ModuleCourse


def auto_enrol_compulsory(user):
    """Enrol a user in all compulsory modules for their course and year.

    Looks up the user's course + year_of_study from their profile,
    finds compulsory ModuleCourse entries, and adds the user to each
    module's students. Skips modules the user is already enrolled in.
    """
    try:
        profile = user.userprofile
    except Exception:
        return

    if not profile.course:
        return

    # Get compulsory modules for this course and year
    year_str = str(profile.year_of_study)
    compulsory_links = ModuleCourse.objects.filter(
        course=profile.course,
        year=year_str,
        is_compulsory=True,
    ).select_related('module')

    for link in compulsory_links:
        # add() is a no-op if the user is already enrolled
        link.module.students.add(user)
