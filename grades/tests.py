from django.test import TestCase
from django.contrib.auth.models import User
from modules.models import Module
from .models import Assignment, Grade


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
