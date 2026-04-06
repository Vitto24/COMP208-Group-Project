from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegistrationForm, EmailLoginForm
from .models import UserProfile
from .utils import (
    enrol_compulsory_only, randomise_optional_modules,
    update_module_selection, CREDITS_PER_SEMESTER,
)
from modules.models import Module, ModuleCourse


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()

            # Create the user profile with course + year
            UserProfile.objects.create(
                user=user,
                course=form.cleaned_data.get('course'),
                year_of_study=form.cleaned_data.get('year_of_study', 1),
            )
            # Only enrol compulsory modules — user picks optionals next
            enrol_compulsory_only(user)

            # Log them in and send to module selection
            login(request, user, backend='accounts.backends.EmailBackend')
            return redirect('accounts:select_modules')
    else:
        form = RegistrationForm()

    return render(request, 'accounts/register.html', {
        'form': form,
        'hide_sidebar': True
    })


@login_required
def select_modules(request):
    """Module selection page shown after registration (or accessible anytime)."""
    profile = request.user.userprofile

    if request.method == 'POST':
        selected_codes = request.POST.getlist('modules')
        success, error = update_module_selection(request.user, selected_codes)
        if success:
            return redirect('/')
        else:
            messages.error(request, error)

    # build year data (same structure as settings page)
    year_data = _build_year_data(request.user, profile)

    return render(request, 'accounts/select_modules.html', {
        'year_data': year_data,
        'profile': profile,
    })


@login_required
def randomise_modules(request):
    """Randomise optional modules to fill 60 credits per semester."""
    if request.method == 'POST':
        randomise_optional_modules(request.user)
    return redirect('accounts:select_modules')


def _build_year_data(user, profile):
    """Build the year -> semester -> module structure for the template."""
    if not profile.course:
        return []

    enrolled_codes = set(
        Module.objects.filter(students=user).values_list('code', flat=True)
    )

    all_years = (
        ModuleCourse.objects.filter(course=profile.course)
        .values_list('year', flat=True)
        .distinct()
    )

    numeric_years = []
    for y in all_years:
        if y.isdigit() and int(y) <= profile.year_of_study:
            numeric_years.append(int(y))

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


def login_view(request):
    if request.method == 'POST':

        form = EmailLoginForm(data=request.POST)

        if form.is_valid():
            user = form.get_user()
            login(request, user)

            if user.is_staff or user.is_superuser:
                return redirect('/admin/')

            return redirect('/')
    else:
        form = EmailLoginForm()

    return render(request, 'accounts/login.html', {
        'form': form,
        'hide_sidebar': True
    })


def logout_view(request):
    logout(request)
    request.session.flush()
    return redirect('accounts:login')
