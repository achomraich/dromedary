from django.core.exceptions import PermissionDenied
from django.test import TestCase
from django.urls import reverse

from tutorials.forms import UserForm
from tutorials.models.models import User, Admin, Student, Tutor, Lesson
from django.contrib.messages import get_messages, ERROR

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

        self.unspecified_user = User.objects.get(username='@jamesdoe')

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

    def test_get_tutors_by_user(self):
        self.client.login(username='@jamesdoe', password='Password123')

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 403)

    def test_get_tutor_details(self):
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.get(reverse('tutor_details', args=[self.tutor1.user.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/manage_tutors/tutor_details.html')
        self.assertContains(response, self.tutor1.user.username)
        self.assertNotContains(response, self.tutor2.user.username)

    def test_get_edit_form(self):
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.get(reverse('tutor_details', args=[self.tutor1.user.id]) + 'edit/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/manage_tutors/edit_tutor.html')
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], UserForm)
        self.assertContains(response, self.tutor1.user.username)
        self.assertNotContains(response, self.tutor2.user.username)

    def test_post_edit_tutor(self):
        updated_username = '@petrap'
        updated_first_name = 'Petraya'
        updated_last_name = 'Peckles'
        updated_email = 'petrapickles@hotmail.com'
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.post(reverse('tutor_details', args=[self.tutor1.user.id]), {
            'entity_id': self.tutor1.user.id,
            'edit': 'edit',
            'username': updated_username,
            'first_name': updated_first_name,
            'last_name': updated_last_name,
            'email': updated_email,
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.url)
        self.tutor1.refresh_from_db()
        self.assertEqual(self.tutor1.user.username, updated_username)
        self.assertEqual(self.tutor1.user.first_name, updated_first_name)
        self.assertEqual(self.tutor1.user.last_name, updated_last_name)
        self.assertEqual(self.tutor1.user.email, updated_email)

    def test_post_edit_tutor_missing_field(self):
        updated_username = '@petrap'
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.post(reverse('tutor_details', args=[self.tutor1.user.id]), {
            'entity_id': self.tutor1.user.id,
            'edit': 'edit',
            'username': updated_username,
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/manage_tutors/edit_tutor.html')
        self.assertContains(
            response,
            "This field is required.",
            html=True
        )
        self.tutor1.refresh_from_db()
        self.assertNotEqual(self.tutor1.user.username, updated_username)

    def test_post_edit_tutor_invalid_username(self):
        updated_username = 'BAD_USERNAME'
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.post(reverse('tutor_details', args=[self.tutor1.user.id]), {
            'entity_id': self.tutor1.user.id,
            'edit': 'edit',
            'username': updated_username,
            'first_name': self.tutor1.user.first_name,
            'last_name': self.tutor1.user.last_name,
            'email': self.tutor1.user.email
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/manage_tutors/edit_tutor.html')
        self.assertContains(
            response,
            "Username must consist of @ followed by at least three alphanumericals",
            html=True
        )
        self.tutor1.refresh_from_db()
        self.assertNotEqual(self.tutor1.user.username, updated_username)

    def test_post_delete_tutor(self):
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.post(reverse('tutor_details', args=[self.tutor1.user.id]), {
            'entity_id': self.tutor1.user.id,
            'delete': 'delete',
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.url)
        self.assertFalse(Tutor.objects.filter(user__username='@petrapickles').exists())
        self.assertFalse(Student.objects.filter(user__username="@petrap").exists())

    def test_post_no_entity_id(self):
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.post(reverse('tutor_details', args=[self.tutor1.user.id]), {
            'edit': 'edit',
            'username': 'newusername',
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.url)

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any(msg.message == "No entity ID provided for the operation." for msg in messages))

        self.assertEqual(messages[0].level, ERROR)

    def test_post_invalid_operation_tutor(self):
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.post(reverse('tutor_details', args=[self.tutor1.user.id]), {
            'entity_id': self.tutor1.user.id,
            'test': 'test',
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.url)

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any(msg.message == "Invalid operation." for msg in messages))

        self.assertEqual(messages[0].level, ERROR)

    def test_get_search_tutor(self):
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.get(self.url, {'search': 'petrapickles'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/manage_tutors/tutors_list.html')
        self.assertContains(response, self.tutor1.user.username)
        self.assertNotContains(response, self.tutor2.user.username)

    def test_get_search_subject(self):
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.get(self.url, {'subject.py': 'Python'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/manage_tutors/tutors_list.html')
        self.assertContains(response, self.tutor1.user.username)