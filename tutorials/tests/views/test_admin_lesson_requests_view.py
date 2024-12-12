from django.test import TestCase, Client
from django.urls import reverse
from tutorials.models import LessonRequest, Student, User, Subject, Term, Status
from datetime import date, timedelta, datetime

class AdminLessonRequestsViewTest(TestCase):

    def setUp(self):

        self.user = User.objects.create_user(
            username='@jane_doe',
            first_name='Jane',
            last_name='Doe',
            email='jane.doe@example.com',
            password='password123'
        )
        self.student = Student.objects.create(user=self.user)
        self.subject1 = Subject.objects.create(name="Python", description="Python Subject")
        self.term = Term.objects.create(start_date=date(2024, 9, 1), end_date=date(2025, 1, 31))
        self.subject2 = Subject.objects.create(name="C++", description="C++ Subject")
        self.term = Term.objects.create(start_date=date(2024, 9, 1), end_date=date(2025, 1, 31))

        self.lesson_request = LessonRequest.objects.create(
            subject=self.subject1,
            time='14:00',
            status=Status.PENDING,
            frequency='W',
            term=self.term,
            start_date=date(2025, 2, 15),
            student=self.student
        )

        self.client = Client()


    def test_admin_lesson_requests_view(self):
        self.client.login(username='@jane_doe', password='password123')
        response = self.client.get(reverse('requests'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student/requests/requests.html')

        self.assertIn('lesson_requests', response.context)
        self.assertEqual(len(response.context['lesson_requests']), 1)
        self.assertEqual(response.context['lesson_requests'][0], self.lesson_request)

    def test_admin_lesson_requests_template_content(self):

        self.client.login(username='@jane_doe', password='password123')
        response = self.client.get(reverse('requests'))


        self.assertEqual(len(response.context['lesson_requests']), 1)
        self.assertContains(response, 'Lesson Requests')
        self.assertEqual(response.context['lesson_requests'][0].subject.name, 'Python')  # Language
        self.assertEqual(str(response.context['lesson_requests'][0].time), "14:00:00")  # Time
        self.assertEqual(response.context['lesson_requests'][0].status, Status.PENDING)  # Length
        self.assertContains(response, 'Weekly') # Status

    def test_no_lesson_requests(self):

        self.client.login(username='@jane_doe', password='password123')
        response = self.client.get(reverse('requests'))

        self.assertContains(response, 'No lesson requests found.')

    def test_multiple_lesson_requests(self):

        self.client.login(username='@jane_doe', password='password123')
        self.lesson_request = LessonRequest.objects.create(
            subject=self.subject2,
            time='14:00',
            status=Status.PENDING,
            frequency='W',
            term=self.term,
            start_date=date(2025, 2, 15),
            student=self.student
        )

        response = self.client.get(reverse('requests'))

        self.assertEqual(len(response.context['lesson_requests']), 2)
        self.assertContains(response, 'Python')
        self.assertContains(response, 'C++')
