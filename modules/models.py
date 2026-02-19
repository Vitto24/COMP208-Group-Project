from django.db import models
from django.contrib.auth.models import User


class Module(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    credits = models.DecimalField(max_digits=4, decimal_places=1)
    lecturer = models.CharField(max_length=200, blank=True)
    semester = models.IntegerField(default=1)
    academic_year = models.CharField(max_length=10, default='2025/26')
    department = models.CharField(max_length=200, blank=True)
    year = models.IntegerField(default=2)
    students = models.ManyToManyField(User, related_name='enrolled_modules', blank=True)

    def __str__(self):
        return f"{self.code}: {self.name}"


class Week(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='weeks')
    number = models.IntegerField()
    title = models.CharField(max_length=200)

    class Meta:
        ordering = ['number']

    def __str__(self):
        return f"{self.module.code} — Week {self.number}: {self.title}"


class Material(models.Model):
    TYPE_CHOICES = [
        ('slides', 'Slides'),
        ('worksheet', 'Worksheet'),
        ('recording', 'Recording'),
        ('other', 'Other'),
    ]

    week = models.ForeignKey(Week, on_delete=models.CASCADE, related_name='materials')
    title = models.CharField(max_length=200)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    url = models.URLField(blank=True)
    available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title} ({self.type})"
