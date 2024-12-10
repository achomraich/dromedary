from django.test import TestCase
from django.urls import reverse
from tutorials.models import Lesson, LessonStatus
from datetime import date, time

class CalendarTestCase(TestCase):

    fixtures = [
        'tutorials/tests/fixtures/default_user.json',
        'tutorials/tests/fixtures/default_tutor.json',
        'tutorials/tests/fixtures/default_student.json',
        'tutorials/tests/fixtures/default_lesson.json',
        'tutorials/tests/fixtures/default_lessonstatus.json'
    ]

    def setUp(self):
        self.url = reverse('calendar')
        self.lesson101 = Lesson.objects.get(pk=101)
        self.lesson102 = Lesson.objects.get(pk=102)

    def test_lesson101_statuses(self):
        """Test LessonStatus records for lesson with pk=101."""
        lesson101_statuses = LessonStatus.objects.filter(lesson_id=self.lesson101)
        self.assertEqual(lesson101_statuses.count(), 3)

        # Verify individual statuses
        scheduled_status = lesson101_statuses.get(pk=101)
        self.assertEqual(scheduled_status.date, date(2025, 2, 1))
        self.assertEqual(scheduled_status.time, time(15, 30))
        self.assertEqual(scheduled_status.status, "Scheduled")
        self.assertEqual(scheduled_status.feedback, "Excellent")
        self.assertFalse(scheduled_status.invoiced)

        pending_status = lesson101_statuses.get(pk=201)
        self.assertEqual(pending_status.date, date(2024, 12, 6))
        self.assertEqual(pending_status.time, time(10, 0))
        self.assertEqual(pending_status.status, "Pending")
        self.assertEqual(pending_status.feedback, "Feedback for pending lesson")
        self.assertFalse(pending_status.invoiced)

        completed_status = lesson101_statuses.get(pk=202)
        self.assertEqual(completed_status.date, date(2024, 12, 5))
        self.assertEqual(completed_status.time, time(14, 0))
        self.assertEqual(completed_status.status, "Completed")
        self.assertEqual(completed_status.feedback, "Feedback for completed lesson")
        self.assertTrue(completed_status.invoiced)

    def test_lesson102_statuses(self):
        """Test LessonStatus records for lesson with pk=102."""
        lesson102_statuses = LessonStatus.objects.filter(lesson_id=self.lesson102)
        self.assertEqual(lesson102_statuses.count(), 1)

        # Verify the single status
        completed_status = lesson102_statuses.get(pk=102)
        self.assertEqual(completed_status.date, date(2025, 5, 1))
        self.assertEqual(completed_status.time, time(15, 30))
        self.assertEqual(completed_status.status, "Completed")
        self.assertEqual(completed_status.feedback, "Good progress")
        self.assertFalse(completed_status.invoiced)
