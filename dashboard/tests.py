from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from accounts.models import UserProfile


class DashboardTest(TestCase):
    def test_dashboard_needs_login(self):
        response = self.client.get(reverse('dashboard:dashboard'))
        self.assertEqual(response.status_code, 302)

    def test_dashboard_loads_for_user(self):
        user = User.objects.create_user(username='d', password='pw')
        UserProfile.objects.create(user=user)
        self.client.force_login(user)
        response = self.client.get(reverse('dashboard:dashboard'))
        self.assertEqual(response.status_code, 200)
