from django.test import TestCase
from tutorials.models import LessonRequest, Student, User, Subject, Term, Status
from datetime import date, timedelta

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
        self.subject = Subject.objects.create(name="Python", description="Python Subject")
        self.term = Term.objects.create(start_date=date(2024, 9, 1), end_date=date(2025, 1, 31))

        self.lesson_request = LessonRequest.objects.create(
            subject=self.subject,
            time='14:00',
            status=Status.PENDING,
            frequency='W',
            term=self.term,
            start_date=date(2025, 2, 15),
            student=self.student
        )

    def test_lesson_request_creation(self):
        self.assertEqual(self.lesson_request.subject.name, 'Python')
        self.assertEqual(self.lesson_request.time, '14:00')
        self.assertEqual(self.lesson_request.term.start_date, date(2024, 9, 1))
        self.assertEqual(self.lesson_request.frequency, 'W')
        self.assertEqual(self.lesson_request.start_date, date(2025, 2, 15))
        self.assertEqual(self.lesson_request.status, Status.PENDING)
