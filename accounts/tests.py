from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from .models import UserProfile
from modules.models import Course


class RegisterTest(TestCase):
    def setUp(self):
        self.course = Course.objects.create(
            name='Computer Science BSc',
            slug='cs',
            degree_level='BSc',
        )

    def test_register_creates_user(self):
        response = self.client.post(reverse('accounts:register'), {
            'first_name': 'Jane',
            'last_name': 'Smith',
            'email': 'jane@liverpool.ac.uk',
            'password1': 'TestPass12345',
            'password2': 'TestPass12345',
            'role': 'student',
            'university': 'uol',
            'course': self.course.id,
            'year_of_study': 1,
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(email='jane@liverpool.ac.uk').exists())

    def test_register_fails_if_passwords_dont_match(self):
        self.client.post(reverse('accounts:register'), {
            'first_name': 'A',
            'last_name': 'B',
            'email': 'ab@liverpool.ac.uk',
            'password1': 'pass123',
            'password2': 'pass456',
            'role': 'student',
            'university': 'uol',
            'year_of_study': 1,
        })
        self.assertFalse(User.objects.filter(email='ab@liverpool.ac.uk').exists())

    def test_student_id_is_generated(self):
        user = User.objects.create_user(username='test1', password='pw')
        profile = UserProfile.objects.create(user=user)
        # should be 8 digits starting with 2
        self.assertEqual(len(profile.student_id), 8)
        self.assertTrue(profile.student_id.startswith('2'))


class LoginTest(TestCase):
    def test_login_with_email(self):
        user = User.objects.create_user(username='x', email='x@liv.ac.uk', password='pw12345')
        UserProfile.objects.create(user=user)
        response = self.client.post(reverse('accounts:login'), {
            'username': 'x@liv.ac.uk',
            'password': 'pw12345',
        })
        self.assertEqual(response.status_code, 302)
