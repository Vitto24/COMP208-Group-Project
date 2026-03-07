from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from modules.models import Course


class RegistrationForm(UserCreationForm):
    """Registration form with course and year selection."""
    course = forms.ModelChoiceField(
        queryset=Course.objects.all(),
        required=False,
        empty_label="-- Select your course --",
    )
    year_of_study = forms.IntegerField(
        min_value=1,
        max_value=6,
        initial=1,
        label="Year of study",
    )

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'course', 'year_of_study']
