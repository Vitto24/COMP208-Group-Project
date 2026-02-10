from django.db import models
from django.contrib.auth.models import User
from modules.models import Module


class Assignment(models.Model):
    TYPE_CHOICES = [
        ('coursework', 'Coursework'),
        ('exam', 'Exam'),
    ]

    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='assignments')
    title = models.CharField(max_length=200)
    weight = models.DecimalField(max_digits=5, decimal_places=1)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    due_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.module.code} — {self.title} ({self.weight}%)"


class Grade(models.Model):
    STATUS_CHOICES = [
        ('graded', 'Graded'),
        ('submitted', 'Submitted'),
        ('not_submitted', 'Not Submitted'),
    ]

    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='grades')
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='grades')
    score = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_submitted')

    def __str__(self):
        return f"{self.student.username} — {self.assignment.title}: {self.score}"
