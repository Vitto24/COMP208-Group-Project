from django.db import models
from django.contrib.auth.models import User


class TimetableEntry(models.Model):
    DAY_CHOICES = [
        ('MON', 'Monday'),
        ('TUE', 'Tuesday'),
        ('WED', 'Wednesday'),
        ('THU', 'Thursday'),
        ('FRI', 'Friday'),
    ]

    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='timetable_entries')
    module = models.ForeignKey('modules.Module', on_delete=models.CASCADE)
    day = models.CharField(max_length=3, choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    room = models.CharField(max_length=100, blank=True)
    event_type = models.CharField(max_length=50, default='Lecture')
    semester = models.IntegerField(default=2)
    weeks = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ['day', 'start_time']

    def __str__(self):
        return f"{self.module.code} — {self.get_day_display()} {self.start_time}"

    @property
    def display_type(self):
        mapping = {
            'PC Teaching Centre': 'Lab',
        }
        return mapping.get(self.event_type, self.event_type)

    @property
    def event_css_class(self):
        mapping = {
            'Lecture': 'event-lecture',
            'Class Test': 'event-lecture',
            'Drop-in': 'event-dropin',
            'Tutorial': 'event-lab',
            'PC Teaching Centre': 'event-lab',
            'Seminar': 'event-seminar',
            'Study': 'event-seminar',
        }
        return mapping.get(self.event_type, 'event-lecture')
