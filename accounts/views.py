from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth import logout 
from .forms import RegistrationForm, EmailLoginForm 
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
        
    return render(request, 'accounts/register.html', {
        'form': form,
        'hide_sidebar': True
    })

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