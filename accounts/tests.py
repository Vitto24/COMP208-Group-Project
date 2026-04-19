from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from .models import UserProfile
from .utils import generate_timetable_for_user
from modules.models import Course, Module, ModuleCourse
from timetable.models import TimetableEntry


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


class RegistrationGateTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='h', password='pw')
        UserProfile.objects.create(user=self.user, registration_complete=False)
        self.client.force_login(self.user)

    def test_incomplete_profile_redirects_to_picker(self):
        r = self.client.get('/', follow=False)
        self.assertEqual(r.status_code, 302)
        self.assertIn('select-modules', r['Location'])

    def test_password_reset_reachable_during_setup(self):
        r = self.client.get(reverse('accounts:password_reset'))
        self.assertEqual(r.status_code, 200)

    def test_staff_bypasses_gate(self):
        self.user.is_staff = True
        self.user.save()
        r = self.client.get('/')
        self.assertNotEqual(r.status_code, 302)


class RolePickerTest(TestCase):
    def setUp(self):
        self.course = Course.objects.create(
            name='Computer Science BSc', slug='cs', degree_level='BSc',
        )

    def _register(self, email, role, **extra):
        data = {
            'first_name': 'T', 'last_name': 'User',
            'email': email,
            'password1': 'TestPass12345', 'password2': 'TestPass12345',
            'role': role,
            'university': 'uol',
        }
        data.update(extra)
        return self.client.post(reverse('accounts:register'), data, follow=False)

    def test_lecturer_gets_staff_and_redirects_to_admin(self):
        r = self._register('lect@liv.ac.uk', 'lecturer')
        self.assertEqual(r.status_code, 302)
        self.assertIn('/admin/', r['Location'])
        u = User.objects.get(email='lect@liv.ac.uk')
        self.assertTrue(u.is_staff)
        self.assertFalse(u.is_superuser)

    def test_admin_gets_superuser(self):
        self._register('adm@liv.ac.uk', 'admin')
        u = User.objects.get(email='adm@liv.ac.uk')
        self.assertTrue(u.is_staff)
        self.assertTrue(u.is_superuser)

    def test_student_with_grant_admin_is_staff(self):
        self._register(
            'self@liv.ac.uk', 'student',
            grant_admin_access='on', course=self.course.id, year_of_study=1,
        )
        u = User.objects.get(email='self@liv.ac.uk')
        self.assertTrue(u.is_staff)
        self.assertFalse(u.userprofile.registration_complete)


class GenerateTimetableTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='gtt', password='pw')
        course = Course.objects.create(name='CS BSc', slug='cs', degree_level='BSc')
        UserProfile.objects.create(user=self.user, course=course, year_of_study=1)
        self.module = Module.objects.create(
            code='COMP101', name='Intro', credits=15, semester=1, year=1,
        )
        ModuleCourse.objects.create(course=course, module=self.module, year='1', is_compulsory=True)
        self.module.students.add(self.user)

    def test_generates_entries_for_new_student(self):
        generate_timetable_for_user(self.user)
        entries = TimetableEntry.objects.filter(student=self.user, module=self.module)
        self.assertTrue(entries.exists())

    def test_rerun_is_idempotent(self):
        generate_timetable_for_user(self.user)
        first = TimetableEntry.objects.filter(student=self.user).count()
        generate_timetable_for_user(self.user)
        second = TimetableEntry.objects.filter(student=self.user).count()
        self.assertEqual(first, second)
