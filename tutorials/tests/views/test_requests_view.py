from datetime import time, timedelta, date

from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse

from tutorials.forms import UserForm, LessonRequestForm
from tutorials.models import LessonRequest, Student, User, Subject, Term, Tutor, Admin, Status


class LessonRequestsViewTest(TestCase):

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
        self.url = reverse('requests')

        self.student = Student.objects.get(user__username='@janedoe')
        self.admin_user = User.objects.get(username='@johndoe')
        self.admin = Admin.objects.create(user=self.admin_user)
        self.tutor1 = Tutor.objects.get(user__username='@petrapickles')
        self.tutor2 = Tutor.objects.get(user__username='@peterpickles')
        self.subject1 = Subject.objects.get(name='Python')
        self.subject2 = Subject.objects.get(name='C++')
        self.term = Term.objects.get(start_date='2024-09-01')

        # Create a lesson request
        self.lesson_request = LessonRequest.objects.create(
            student=self.student,
            subject=self.subject1,
            term=self.term,
            time=time(10, 0),
            start_date='2024-12-18',
            duration=timedelta(hours=1),
            frequency='W',
            status='Pending'
        )

    def test_unauthenticated_access(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"{reverse('log_in')}?next={self.url}")


    def test_student_lesson_requests_view(self):
        self.client.login(username='@janedoe', password='Password123')
        # Access the view
        response = self.client.get(self.url)

        # Check that the response is OK
        self.assertEqual(response.status_code, 200)

        # Check that the correct template is used
        self.assertTemplateUsed(response, 'shared/requests/requests.html')

        # Check that the lesson request is in the context
        self.assertIn('lesson_requests', response.context)
        self.assertEqual(len(response.context['lesson_requests']), 1)
        self.assertEqual(response.context['lesson_requests'][0], self.lesson_request)

    def test_admin_lesson_requests_view(self):
        self.client.login(username='@johndoe', password='Password123')

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shared/requests/requests.html')
        self.assertIn('lesson_requests', response.context)
        self.assertEqual(len(response.context['lesson_requests']), LessonRequest.objects.count())

    def test_tutor_lesson_requests_view(self):
        self.client.login(username='@petrapickles', password='Password123')
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('dashboard'))

    def test_assign_tutor(self):
        self.client.login(username='@johndoe', password='Password123')

        # POST to assign a tutor
        response = self.client.post(reverse('request_assign', args=[self.lesson_request.pk]), {
            'request_id': self.lesson_request.pk,
            'edit': 'edit',
            'tutor': self.tutor2.user.id,
            'price_per_lesson': '50'
        })

        self.assertEqual(response.status_code, 302)
        self.lesson_request.refresh_from_db()
        self.assertEqual(self.lesson_request.status, Status.CONFIRMED)

    def test_invalid_form_assign_tutor(self):
        self.client.login(username='@johndoe', password='Password123')

        # POST to assign a tutor
        response = self.client.post(reverse('request_assign', args=[self.lesson_request.pk]), {
            'request_id': self.lesson_request.pk,
            'edit': 'edit',
            'tutor': self.tutor1.user.id,
            'price_per_lesson': '50'
        })

        self.assertEqual(response.status_code, 200)
        self.lesson_request.refresh_from_db()
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any(msg.message == "Failed to update details. Please correct the errors and try again." for msg in messages))
        self.assertEqual(self.lesson_request.status, Status.PENDING)

    def test_reject_request(self):
        self.client.login(username='@johndoe', password='Password123')

        # POST to reject a request
        response = self.client.post(self.url, {
            'request_id': self.lesson_request.id,
            'reject': 'true'
        })

        self.assertEqual(response.status_code, 302)
        self.lesson_request.refresh_from_db()
        self.assertEqual(self.lesson_request.status, Status.REJECTED)

    def test_cancel_request(self):
        self.client.login(username='@janedoe', password='Password123')

        # POST to cancel a request
        response = self.client.post(self.url, {
            'request_id': self.lesson_request.id,
            'cancel': 'true'
        })

        self.assertEqual(response.status_code, 302)
        self.lesson_request.refresh_from_db()
        self.assertEqual(self.lesson_request.status, Status.CANCELLED)

    def test_invalid_post_action(self):
        self.client.login(username='@johndoe', password='Password123')

        # POST with an invalid action
        response = self.client.post(self.url, {
            'request_id': self.lesson_request.id,
            'unknown_action': 'true'
        })

        self.assertEqual(response.status_code, 302)

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any(msg.message == "Invalid operation." for msg in messages))

    def test_null_request_id(self):
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.post(self.url, {})

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('requests'))
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any(msg.message == "No entity ID provided for the operation." for msg in messages))

    def test_request_assign_no_existing_form(self):
        self.client.login(username='@johndoe', password='Password123')
        response = self.client.get(reverse('request_assign', args=[self.lesson_request.pk]),
            {'request_id': self.lesson_request.pk}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)

    def test_request_assign_page(self):
        self.client.login(username='@johndoe', password='Password123')

        # Access the request assign page
        assign_url = reverse('request_assign', kwargs={'request_id': self.lesson_request.id})
        response = self.client.get(assign_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/requests/assign_tutor.html')
        self.assertIn('form', response.context)
        self.assertEqual(response.context['request'], self.lesson_request)

    def test_student_lesson_requests_template_content(self):
        self.client.login(username='@janedoe', password='Password123')
        # Access the admin_lesson_requests view
        response = self.client.get(self.url)

        # Check for content in the rendered template
        self.assertContains(response, 'Lesson Requests')
        self.assertContains(response, 'Python')  # Language
        self.assertContains(response, 'Weekly')  # Frequency (convert frequency choice in template)
        self.assertContains(response, 'Pending')  # Status

    def test_no_lesson_requests(self):
        self.client.login(username='@janedoe', password='Password123')
        LessonRequest.objects.all().delete()  # Clear any existing data
        response = self.client.get(self.url)

        # Check for the "No lesson requests found" message
        self.assertContains(response, 'No lesson requests found.')

    def test_multiple_lesson_requests(self):
        self.client.login(username='@janedoe', password='Password123')
        # Add another lesson request
        LessonRequest.objects.create(
            student=self.student,
            subject=self.subject2,
            time='11:00:00',
            duration=timedelta(hours=2),
            term=self.term,
            start_date='2024-12-15',
            frequency='F',
            status='Approved'
        )

        response = self.client.get(self.url)

        # Check that all lesson requests are displayed
        self.assertEqual(len(response.context['lesson_requests']), 2)
        self.assertContains(response, 'Python')
        self.assertContains(response, 'C++')

    def test_get_make_request_form(self):
        self.client.login(username='@janedoe', password='Password123')

        response = self.client.get(reverse('lesson_request'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student/requests/lesson_request_form.html')
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], LessonRequestForm)

    def test_post_make_request_form(self):
        self.client.login(username='@janedoe', password='Password123')
        self.term2 = Term.objects.create(
            term_name=1,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 3, 31)
        )
        response = self.client.post(reverse('lesson_request'), {
            'subject': self.subject1.id,
            'term': self.term2.id,
            'start_date': '2025-1-19',
            'time': time(10, 0),
            'duration': timedelta(hours=1),
            'frequency': 'W',
        })

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('requests'))
        self.assertEqual(LessonRequest.objects.count(), 2)

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any(msg.message == "Request submitted successfully." for msg in messages))

    def test_post_make_invalid_request_form(self):
        self.client.login(username='@janedoe', password='Password123')
        self.term2 = Term.objects.create(
            term_name=1,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 3, 31)
        )
        response = self.client.post(reverse('lesson_request'), {
            'subject': self.subject1.id,
            'term': self.term2.id,
            'start_date': '2024-1-19',
            'time': time(10, 0),
            'duration': timedelta(hours=1),
            'frequency': 'W',
        })

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student/requests/lesson_request_form.html')
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], LessonRequestForm)

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any(msg.message == "Failed to update details. Please correct the errors and try again." for msg in messages))

