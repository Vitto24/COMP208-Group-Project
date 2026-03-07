from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from modules.models import Course


class RegistrationForm(UserCreationForm):
    """Registration form with course and year selection."""
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True, label="University Email")

    course = forms.ModelChoiceField(
        queryset=Course.objects.all(),
        required=False,
        empty_label="-- Select your course --",
    )
    year_of_study = forms.IntegerField(
        min_value=1,
        max_value=4,
        initial=1,
        label="Year of study",
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email',
                  'password1', 'password2', 'course', 'year_of_study']

    def save(self, commit=True):
        user = super().save(commit=False)
        # Auto-generate a username from the email prefix
        email_prefix = self.cleaned_data['email'].split('@')[0]
        username = email_prefix
        # Handle duplicates by appending a number
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{email_prefix}{counter}"
            counter += 1
        user.username = username
        if commit:
            user.save()
        return user
