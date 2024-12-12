"""Tests of the home view."""
from django.test import TestCase
from django.urls import reverse
from tutorials.models import User, Student

class HomeViewTestCase(TestCase):
    """Tests of the home view."""
    fixtures = [
        'tutorials/tests/fixtures/default_user.json',
        'tutorials/tests/fixtures/other_users.json',
        'tutorials/tests/fixtures/default_tutor.json',
        'tutorials/tests/fixtures/default_student.json',
        'tutorials/tests/fixtures/default_lesson.json',
        'tutorials/tests/fixtures/default_subject.json',
        'tutorials/tests/fixtures/default_term.json',
        'tutorials/tests/fixtures/default_availability.json'
    ]
    def setUp(self):
        self.url = reverse('home')
        self.user = User.objects.get(username='@johndoe')
        self.student = Student.objects.get(user__username='@charlie')


    def test_home_url(self):
        self.assertEqual(self.url,'/')

    def test_get_home(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

    def test_get_home_redirects_when_logged_in(self):
        self.client.login(username=self.student.user.username, password="Password123")
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('dashboard')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'student/student_dashboard.html')