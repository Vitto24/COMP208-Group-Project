import uuid
from django.db import models
from django.contrib.auth.models import User
from modules.models import Course


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('lecturer', 'Lecturer'),
        ('admin', 'Admin'),
    ]

    UNIVERSITY_CHOICES = [
        ('uol', 'University of Liverpool'),
        ('ljmu', 'Liverpool John Moores University'),
        ('chester', 'University of Chester'),
        ('edge_hill', 'Edge Hill University'),
    ]

    STUDY_LEVEL_CHOICES = [
        ('undergraduate', 'Undergraduate'),
        ('postgraduate', 'Postgraduate'),
    ]

    UNIVERSITY_URLS = {
        'uol': 'https://my.liverpool.ac.uk/',
        'ljmu': 'https://www.ljmu.ac.uk/',
        'chester': 'https://www.chester.ac.uk/',
        'edge_hill': 'https://www.edgehill.ac.uk/',
    }

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    university = models.CharField(
        max_length=50,
        choices=UNIVERSITY_CHOICES,
        default='uol',
        blank=True,
    )
    study_level = models.CharField(
        max_length=20,
        choices=STUDY_LEVEL_CHOICES,
        default='undergraduate',
    )
    course = models.ForeignKey(Course, null=True, blank=True, on_delete=models.SET_NULL)
    year_of_study = models.IntegerField(default=1)
    student_id = models.CharField(max_length=10, unique=True, blank=True)
    # set to False on fresh registration until the student finishes the module picker
    registration_complete = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        # Auto-generate a student ID on first save if not already set
        if not self.student_id:
            self.student_id = self._generate_student_id()
        super().save(*args, **kwargs)

    def _generate_student_id(self):
        """Generate a unique 8-digit numeric student ID."""
        while True:
            # Random 8-digit number starting with 2 (e.g. 20xxxxxx)
            candidate = '2' + str(uuid.uuid4().int)[:7]
            if not UserProfile.objects.filter(student_id=candidate).exists():
                return candidate

    @property
    def university_url(self):
        return self.UNIVERSITY_URLS.get(self.university, 'https://my.liverpool.ac.uk/')

    @property
    def university_display(self):
        return dict(self.UNIVERSITY_CHOICES).get(self.university, 'University of Liverpool')

    def __str__(self):
        return f"{self.user.username} ({self.role})"
