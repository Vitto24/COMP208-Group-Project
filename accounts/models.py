from django.db import models
from django.contrib.auth.models import User
from modules.models import Course


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('lecturer', 'Lecturer'),
        ('admin', 'Admin'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    university = models.CharField(max_length=200, blank=True)
    course = models.ForeignKey(Course, null=True, blank=True, on_delete=models.SET_NULL)
    year_of_study = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.user.username} ({self.role})"
