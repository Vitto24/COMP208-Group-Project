import datetime
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from modules.models import Module
from accounts.models import UserProfile
from timetable.models import TimetableEntry
from .models import Assignment, Grade, Submission


class GradesTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='s1', password='pw')
        self.module = Module.objects.create(
            code='COMP208', name='GSD', credits=15, semester=2, year=2,
        )
        self.ca1 = Assignment.objects.create(
            module=self.module, title='Requirements', weight=12, type='coursework',
        )
        self.ca2 = Assignment.objects.create(
            module=self.module, title='Demo', weight=15, type='coursework',
        )

    def test_grade_score_can_be_blank(self):
        grade = Grade.objects.create(
            student=self.user, assignment=self.ca1, status='not_submitted',
        )
        self.assertIsNone(grade.score)

    def test_assignment_has_correct_module(self):
        self.assertEqual(self.ca1.module.code, 'COMP208')

    def test_weighted_average(self):
        # 80 on weight 12 + 60 on weight 15 = 1860 / 27 = 68.888...
        Grade.objects.create(student=self.user, assignment=self.ca1, score=80, status='graded')
        Grade.objects.create(student=self.user, assignment=self.ca2, score=60, status='graded')
        graded = Grade.objects.filter(student=self.user, status='graded')
        total_weight = sum(g.assignment.weight for g in graded)
        weighted_sum = sum(g.score * g.assignment.weight for g in graded)
        average = weighted_sum / total_weight
        self.assertAlmostEqual(float(average), 68.88, places=1)


class SubmissionTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='s2', password='pw')
        UserProfile.objects.create(user=self.user)
        self.module = Module.objects.create(
            code='COMP208', name='GSD', credits=15, semester=2, year=2,
        )
        self.module.students.add(self.user)
        self.assignment = Assignment.objects.create(
            module=self.module, title='Design', weight=15, type='coursework',
            due_date=datetime.date(2026, 5, 1),
        )
        self.client.force_login(self.user)

    def test_submit_creates_row(self):
        self.client.post(reverse('grades:submit_assignment', args=[self.assignment.id]))
        self.assertTrue(
            Submission.objects.filter(student=self.user, assignment=self.assignment).exists()
        )

    def test_double_submit_is_idempotent(self):
        self.client.post(reverse('grades:submit_assignment', args=[self.assignment.id]))
        self.client.post(reverse('grades:submit_assignment', args=[self.assignment.id]))
        count = Submission.objects.filter(student=self.user, assignment=self.assignment).count()
        self.assertEqual(count, 1)

    def test_staff_mark_sets_score_and_status(self):
        self.user.is_staff = True
        self.user.save()
        self.client.post(reverse('grades:mark_assignment', args=[self.assignment.id]), {'score': '72'})
        grade = Grade.objects.get(student=self.user, assignment=self.assignment)
        self.assertEqual(float(grade.score), 72.0)
        self.assertEqual(grade.status, 'graded')

    def test_non_staff_cant_mark(self):
        self.client.post(reverse('grades:mark_assignment', args=[self.assignment.id]), {'score': '72'})
        self.assertFalse(
            Grade.objects.filter(student=self.user, assignment=self.assignment, status='graded').exists()
        )


class IcalExportTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='cal', password='pw')
        UserProfile.objects.create(user=self.user)
        module = Module.objects.create(
            code='COMP101', name='Intro', credits=15, semester=1, year=1,
        )
        TimetableEntry.objects.create(
            student=self.user, module=module, day='MON',
            start_time=datetime.time(9), end_time=datetime.time(10),
            event_type='Lecture', semester=1, weeks='1-12',
        )
        self.client.force_login(self.user)

    def test_export_returns_ical(self):
        r = self.client.get(reverse('timetable:export_ical'))
        self.assertEqual(r.status_code, 200)
        self.assertIn('text/calendar', r['content-type'])

    def test_export_contains_vevent(self):
        r = self.client.get(reverse('timetable:export_ical'))
        body = r.content.decode('utf-8')
        self.assertIn('BEGIN:VCALENDAR', body)
        self.assertIn('BEGIN:VEVENT', body)
