from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from accounts.models import UserProfile
from .models import Module


class ModuleTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='bob', password='pass')
        UserProfile.objects.create(user=self.user)
        self.module = Module.objects.create(
            code='COMP208',
            name='Group Software Development',
            credits=15,
            semester=2,
            year=2,
        )
        self.module.students.add(self.user)

    def test_module_detail_loads(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('modules:module_detail', args=['COMP208']))
        self.assertEqual(response.status_code, 200)

    def test_missing_module_returns_404(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('modules:module_detail', args=['FAKE999']))
        self.assertEqual(response.status_code, 404)
