from django.test import TestCase
from django.urls import reverse
from tutorials.models import LessonRequest, Student, User

class AdminLessonRequestsViewTest(TestCase):
    def setUp(self):
        # Create a user and student
        self.user = User.objects.create_user(
            username='@jane_doe',
            first_name='Jane',
            last_name='Doe',
            email='jane.doe@example.com',
            password='password123'
        )
        self.student = Student.objects.create(user=self.user)

        # Create a lesson request
        self.lesson_request = LessonRequest.objects.create(
            student=self.student,
            language='python',
            lesson_time='10:00',
            lesson_day='tue',
            lesson_length=45,
            lesson_frequency='1',
            status='pending'
        )

    def test_admin_lesson_requests_view(self):
        # Access the admin_lesson_requests view
        response = self.client.get(reverse('admin_lesson_requests'))

        # Check that the response is OK
        self.assertEqual(response.status_code, 200)

        # Check that the correct template is used
        self.assertTemplateUsed(response, 'admin_lesson_requests.html')

        # Check that the lesson request is in the context
        self.assertIn('lesson_requests', response.context)
        self.assertEqual(len(response.context['lesson_requests']), 1)
        self.assertEqual(response.context['lesson_requests'][0], self.lesson_request)

    def test_admin_lesson_requests_template_content(self):
        # Access the admin_lesson_requests view
        response = self.client.get(reverse('admin_lesson_requests'))

        # Check for content in the rendered template
        self.assertContains(response, 'Lesson Requests')
        self.assertContains(response, 'Python')  # Language
        self.assertContains(response, 'Tuesday')  # Day
        self.assertContains(response, '10:00')  # Time
        self.assertContains(response, '45')  # Length
        self.assertContains(response, 'Weekly')  # Frequency (convert frequency choice in template)
        self.assertContains(response, 'pending')  # Status

    def test_no_lesson_requests(self):
        LessonRequest.objects.all().delete()  # Clear any existing data
        response = self.client.get(reverse('admin_lesson_requests'))

        # Check for the "No lesson requests found" message
        self.assertContains(response, 'No lesson requests found.')

    def test_multiple_lesson_requests(self):
        # Add another lesson request
        LessonRequest.objects.create(
            student=self.student,
            language='java',
            lesson_time='11:00',
            lesson_day='wed',
            lesson_length=30,
            lesson_frequency='2',
            status='approved'
        )

        response = self.client.get(reverse('admin_lesson_requests'))

        # Check that all lesson requests are displayed
        self.assertEqual(len(response.context['lesson_requests']), 2)
        self.assertContains(response, 'Python')
        self.assertContains(response, 'Java')