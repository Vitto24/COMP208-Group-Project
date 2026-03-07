from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from modules.models import Course
from accounts.models import UserProfile
from accounts.utils import auto_enrol_compulsory


@login_required
def settings_view(request):
    # Make sure the user has a profile
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        # Update basic user info
        request.user.first_name = request.POST.get('first_name', '')
        request.user.last_name = request.POST.get('last_name', '')
        request.user.email = request.POST.get('email', '')
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

        # Re-run auto-enrolment to pick up any new compulsory modules
        auto_enrol_compulsory(request.user)

        messages.success(request, 'Settings saved.')
        return redirect('settings_page:settings')

    courses = Course.objects.all().order_by('name')

    context = {
        'profile': profile,
        'courses': courses,
    }
    return render(request, 'settings_page/settings.html', context)
