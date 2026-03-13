from django.shortcuts import render, redirect
from .forms import RegistrationForm
from .models import UserProfile
from .utils import auto_enrol_compulsory


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

            # Auto-enrol in compulsory modules
            auto_enrol_compulsory(user)

            return redirect('accounts:login')
    else:
        form = RegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})
