from django.test import TestCase
from tutorials.models import LessonRequest, Student, User

class LessonRequestModelTest(TestCase):
    def setUp(self):
        # Create a user and student for testing
        self.user = User.objects.create_user(
            username='@john_doe',
            first_name='John',
            last_name='Doe',
            email='john.doe@example.com',
            password='password123'
        )
        self.student = Student.objects.create(user=self.user)

        # Create a lesson request
        self.lesson_request = LessonRequest.objects.create(
            student=self.student,
            language='python',
            lesson_time='14:00',
            lesson_day='mon',
            lesson_length=60,
            lesson_frequency='1',
            status='pending'
        )

    def test_lesson_request_creation(self):
        self.assertEqual(self.lesson_request.student, self.student)
        self.assertEqual(self.lesson_request.language, 'python')
        self.assertEqual(self.lesson_request.lesson_time.strftime('%H:%M'), '14:00')
        self.assertEqual(self.lesson_request.lesson_day, 'mon')
        self.assertEqual(self.lesson_request.lesson_length, 60)
        self.assertEqual(self.lesson_request.lesson_frequency, '1')
        self.assertEqual(self.lesson_request.status, 'pending')
