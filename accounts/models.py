from django.db import models
from django.contrib.auth.models import User
from modules.models import Course
import random


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('lecturer', 'Lecturer'),
        ('admin', 'Admin'),
    ]

    UNIVERSITY_CHOICES = [
        ('UOL', 'University of Liverpool'),
        ('LJMU', 'Liverpool John Moores University'),
        ('HOPE', 'Liverpool Hope University'),
    ]

    LEVEL_CHOICES = [
        ('UG', 'Undergraduate'),
        ('PG', 'Postgraduate'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    university = models.CharField(max_length=10, choices=UNIVERSITY_CHOICES, default='UOL')
    course = models.ForeignKey(Course, null=True, blank=True, on_delete=models.SET_NULL)
    year_of_study = models.IntegerField(default=1)

    student_id = models.CharField(max_length=10, editable=False, null=True, blank=True)
    degree_level = models.CharField(max_length=2, choices=LEVEL_CHOICES, default='UG')

    def __str__(self):
        return f"{self.user.username} ({self.role})"
    
    def save(self, *args, **kwargs):
        if not self.student_id:
            self.student_id = ''.join([str(random.randint(0, 9)) for _ in range (8)])
        super().save(*args, **kwargs)

