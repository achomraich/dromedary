"""Tests for the dashboard view."""
from django.contrib import messages
from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse
from tutorials.forms import UserForm
from tutorials.models import User, Admin, Student, Tutor
from tutorials.tests.helpers import reverse_with_next

class DashboardViewTest(TestCase):
    """Test suite for the dashboard view."""

    fixtures = [
        'tutorials/tests/fixtures/default_user.json',
        'tutorials/tests/fixtures/other_users.json',
        'tutorials/tests/fixtures/default_student.json',
        'tutorials/tests/fixtures/default_tutor.json',
    ]

    def setUp(self):
        self.admin_user = User.objects.get(username='@johndoe')
        self.admin = Admin.objects.create(user=self.admin_user)
        self.tutor_user = User.objects.get(username='@petrapickles')
        self.tutor = Tutor.objects.get(user__username='@petrapickles')
        self.student = Student.objects.get(user__username='@charlie')
        self.student.has_new_lesson_notification = True
        self.student.save()
        self.student_user2 = User.objects.get(username='@janedoe')
        self.student2 = Student.objects.get(user=self.student_user2)
        self.url = reverse('dashboard')

    def test_dashboard_url(self):
        self.client.login(username=self.admin_user.username, password='Password123')
        self.assertEqual(self.url, '/dashboard/')

    def test_get_dashboard_admin(self):
        self.client.login(username=self.admin_user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/admin_dashboard.html')

    def test_get_dashboard_tutor(self):
        self.client.login(username=self.tutor_user.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tutor/tutor_dashboard.html')

    def test_get_dashboard_student(self):
        self.client.login(username=self.student_user2.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student/student_dashboard.html')

    def test_get_dashboard_student_new_notif(self):
        self.client.login(username=self.student.user.username, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student/student_dashboard.html')
        self.assertTrue(self.student.has_new_lesson_notification)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any(msg.message == "There has been an update to your lesson requests!" for msg in messages))


