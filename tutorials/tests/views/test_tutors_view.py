from django.test import TestCase
from django.urls import reverse
from tutorials.models import User, Admin, Student, Tutor, Lesson

class TutorsTestCase(TestCase):

    fixtures = [
        'tutorials/tests/fixtures/default_user.json',
        'tutorials/tests/fixtures/other_users.json',
        'tutorials/tests/fixtures/default_tutor.json',
        'tutorials/tests/fixtures/default_student.json',
        'tutorials/tests/fixtures/default_lesson.json',
        'tutorials/tests/fixtures/default_subject.json',
        'tutorials/tests/fixtures/default_term.json'
    ]

    def setUp(self):
        self.url = reverse('tutors_list')

        self.admin_user = User.objects.get(username='@johndoe')
        self.admin = Admin.objects.create(user=self.admin_user)

        self.student = Student.objects.get(user__username='@janedoe')

        self.tutor1 = Tutor.objects.get(user__username='@petrapickles')
        self.tutor2 = Tutor.objects.get(user__username='@peterpickles')

        self.lesson = Lesson.objects.get(pk=1)

    def test_tutors_url(self):
        self.assertEqual(self.url,'/dashboard/tutors/')

    def test_get_tutors_by_admin(self):
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/manage_tutors/tutors_list.html')
        self.assertContains(response, self.tutor1.user.username)
        self.assertContains(response, self.tutor2.user.username)

    def test_get_tutors_by_student(self):
        self.client.login(username='@janedoe', password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student/my_tutors/tutors_list.html')
        self.assertContains(response, self.tutor1.user.username)
        self.assertNotContains(response, self.tutor2.user.username)

    def test_tutor_details(self):
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.get(reverse('tutor_details', args=[self.tutor1.user.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/manage_tutors/tutor_details.html')
        self.assertContains(response, self.tutor1.user.username)
        self.assertContains(response, self.tutor2.user.username)
