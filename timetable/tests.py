import datetime
from django.test import TestCase
from django.contrib.auth.models import User
from modules.models import Module
from .models import TimetableEntry


class TimetableTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='t1', password='pw')
        self.module = Module.objects.create(
            code='TEST101', name='Test', credits=15, semester=1, year=1,
        )

    def test_only_own_entries_visible(self):
        other = User.objects.create_user(username='t2', password='pw')
        TimetableEntry.objects.create(
            student=self.user, module=self.module, day='MON',
            start_time=datetime.time(9, 0), end_time=datetime.time(10, 0),
        )
        TimetableEntry.objects.create(
            student=other, module=self.module, day='TUE',
            start_time=datetime.time(11, 0), end_time=datetime.time(12, 0),
        )
        mine = TimetableEntry.objects.filter(student=self.user)
        self.assertEqual(mine.count(), 1)

    def test_semester_filter(self):
        TimetableEntry.objects.create(
            student=self.user, module=self.module, day='WED',
            start_time=datetime.time(13, 0), end_time=datetime.time(14, 0),
            semester=1,
        )
        TimetableEntry.objects.create(
            student=self.user, module=self.module, day='WED',
            start_time=datetime.time(13, 0), end_time=datetime.time(14, 0),
            semester=2,
        )
        sem1 = TimetableEntry.objects.filter(student=self.user, semester=1)
        self.assertEqual(sem1.count(), 1)
