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
        self.url = reverse('students_list')

        self.admin_user = User.objects.get(username='@johndoe')
        self.admin = Admin.objects.create(user=self.admin_user)

        self.tutor = Tutor.objects.get(user__username='@petrapickles')

        self.student1 = Student.objects.get(user__username='@janedoe')
        self.student2 = Student.objects.get(user__username='@rogersmith')

        self.lesson = Lesson.objects.get(pk=1)

    def test_tutors_url(self):
        self.assertEqual(self.url,'/dashboard/tutors/')

    def test_get_students_by_admin(self):
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/manage_students/students_list.html')
        self.assertContains(response, self.student1.user.username)
        self.assertContains(response, self.student2.user.username)

    def test_get_students_by_tutor(self):
        self.client.login(username='@petrapickles', password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tutor/my_students/tutors_list.html')
        self.assertContains(response, self.student1.user.username)
        self.assertNotContains(response, self.student2.user.username)

    def test_student_details(self):
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.get(reverse('student_details', args=[self.student1.user.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/manage_students/students_details.html')
        self.assertContains(response, self.student1.user.username)
        self.assertContains(response, self.student2.user.username)
