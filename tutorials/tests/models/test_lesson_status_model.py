from django.test import TestCase
from tutorials.models import LessonStatus, Lesson, Tutor, Student, Subject, Term, Status, User
from datetime import date, time, timedelta
from django.core.exceptions import ValidationError

class LessonStatusModelTestCase(TestCase):

    def setUp(self):
        self.tutor = Tutor.objects.create(user=User.objects.create(username="tutor1", email="tutor1@example.com"))
        self.student = Student.objects.create(user=User.objects.create(username="student1", email="student1@example.com"))
        self.subject = Subject.objects.create(name="Python", description="Basic Python")
        self.term = Term.objects.create(start_date=date(2024, 9, 1), end_date=date(2024, 12, 31))
        self.lesson = Lesson.objects.create(
            tutor=self.tutor,
            student=self.student,
            subject_id=self.subject,
            term_id=self.term,
            frequency="W",
            duration=timedelta(hours=1),
            start_date=date(2023, 9, 15),
            price_per_lesson=50,
        )

    def test_create_valid_lesson_status(self):
        """Test creating a valid LessonStatus."""
        lesson_status = LessonStatus.objects.create(
            lesson_id=self.lesson,
            date=date(2023, 9, 15),
            time=time(10, 30),
            status=Status.BOOKED,
            feedback="Great session",
            invoiced=True,
        )
        self.assertEqual(lesson_status.status, Status.COMPLETED)
        self.assertEqual(lesson_status.feedback, "Great session")
        self.assertTrue(lesson_status.invoiced)

    def test_invalid_status_choice(self):
        """Test that an invalid status choice raises a ValidationError."""
        with self.assertRaises(ValidationError):
            lesson_status = LessonStatus(
                lesson_id=self.lesson,
                date=date(2023, 9, 15),
                time=time(10, 30),
                status="INVALID",  # Invalid choice
            )
            lesson_status.full_clean()  # Trigger validation

    def test_blank_feedback(self):
        """Test that feedback defaults to an empty string."""
        lesson_status = LessonStatus.objects.create(
            lesson_id=self.lesson,
            date=date(2023, 9, 15),
            time=time(10, 30),
            status=Status.COMPLETED,
        )
        self.assertEqual(lesson_status.feedback, "")

    def test_default_invoiced(self):
        """Test that invoiced defaults to False."""
        lesson_status = LessonStatus.objects.create(
            lesson_id=self.lesson,
            date=date(2023, 9, 15),
            time=time(10, 30),
            status=Status.PENDING,
        )
        self.assertFalse(lesson_status.invoiced)

    def test_missing_date(self):
        """Test that a LessonStatus cannot be created without a date."""
        with self.assertRaises(ValidationError):
            lesson_status = LessonStatus(
                lesson_id=self.lesson,
                time=time(10, 30),
                status=Status.PENDING,
            )
            lesson_status.full_clean()  # Trigger validation

    def test_missing_time(self):
        """Test that a LessonStatus cannot be created without a time."""
        with self.assertRaises(ValidationError):
            lesson_status = LessonStatus(
                lesson_id=self.lesson,
                date=date(2023, 9, 15),
                status=Status.PENDING,
            )
            lesson_status.full_clean()  # Trigger validation

    def test_missing_lesson_id(self):
        """Test that a LessonStatus cannot be created without a lesson."""
        with self.assertRaises(ValidationError):
            lesson_status = LessonStatus(
                date=date(2023, 9, 15),
                time=time(10, 30),
                status=Status.PENDING,
            )
            lesson_status.full_clean()

    def test_future_date(self):
        """Test that a LessonStatus can have a future date."""
        future_date = date(2024, 1, 1)
        lesson_status = LessonStatus.objects.create(
            lesson_id=self.lesson,
            date=future_date,
            time=time(10, 30),
            status=Status.BOOKED,
        )
        self.assertEqual(lesson_status.date, future_date)

    def test_past_date(self):
        """Test that a LessonStatus can have a past date."""
        past_date = date(2022, 1, 1)
        lesson_status = LessonStatus.objects.create(
            lesson_id=self.lesson,
            date=past_date,
            time=time(10, 30),
            status=Status.COMPLETED,
        )
        self.assertEqual(lesson_status.date, past_date)

    def test_future_date_with_feedback(self):
        """Test that feedback is cleared for future dates."""
        future_date = date.today() + timedelta(days=30)
        lesson_status = LessonStatus.objects.create(
            lesson_id=self.lesson,
            date=future_date,
            time=time(10, 30),
            status=Status.BOOKED,
            feedback="This should be cleared",  # Non-empty feedback
        )
        self.assertEqual(lesson_status.feedback, "")

    def test_past_date_pending_status(self):
        """Test that past dates with PENDING status are changed to CANCELLED."""
        past_date = date.today() - timedelta(days=30)
        lesson_status = LessonStatus.objects.create(
            lesson_id=self.lesson,
            date=past_date,
            time=time(10, 30),
            status=Status.PENDING,
        )
        self.assertEqual(lesson_status.status, Status.CANCELLED)  # Status should be updated

    def test_past_date_booked_status(self):
        """Test that past dates with BOOKED status are changed to COMPLETED."""
        past_date = date.today() - timedelta(days=30)
        lesson_status = LessonStatus.objects.create(
            lesson_id=self.lesson,
            date=past_date,
            time=time(10, 30),
            status=Status.BOOKED,
        )
        self.assertEqual(lesson_status.status, Status.COMPLETED)  # Status should be updated

    def test_future_date_empty_feedback(self):
        """Test that feedback remains empty for future dates when initially empty."""
        future_date = date.today() + timedelta(days=30)
        lesson_status = LessonStatus.objects.create(
            lesson_id=self.lesson,
            date=future_date,
            time=time(10, 30),
            status=Status.BOOKED,
        )
        self.assertEqual(lesson_status.feedback, "")  # Feedback should remain empty

    def test_today_date(self):
        """Test that feedback is not cleared for today."""
        today = date.today()
        lesson_status = LessonStatus.objects.create(
            lesson_id=self.lesson,
            date=today,
            time=time(10, 30),
            status=Status.BOOKED,
            feedback="Feedback should remain",
        )
        self.assertEqual(lesson_status.feedback, "Feedback should remain")  # Feedback should not be cleared

    def test_feedback_empty_for_future_and_past_dates(self):
        """Test that feedback remains empty for both future and past dates if it's already empty."""
        future_date = date.today() + timedelta(days=30)
        past_date = date.today() - timedelta(days=30)

        # For future date with empty feedback
        lesson_status_future = LessonStatus.objects.create(
            lesson_id=self.lesson,
            date=future_date,
            time=time(10, 30),
            status=Status.BOOKED,
            feedback="",  # Empty feedback
        )
        self.assertEqual(lesson_status_future.feedback, "")  # Feedback should remain empty

        # For past date with empty feedback
        lesson_status_past = LessonStatus.objects.create(
            lesson_id=self.lesson,
            date=past_date,
            time=time(10, 30),
            status=Status.BOOKED,
            feedback="",  # Empty feedback
        )
        self.assertEqual(lesson_status_past.feedback, "")  # Feedback should remain empty

    def test_future_date_with_non_empty_feedback(self):
        """Test that feedback is cleared when the date is in the future and feedback is non-empty."""
        future_date = date.today() + timedelta(days=30)
        lesson_status = LessonStatus(
            lesson_id=self.lesson,
            date=future_date,
            time=time(10, 30),
            status=Status.BOOKED,
            feedback="This should be cleared",  # Non-empty feedback
        )
        lesson_status.full_clean()  # Explicitly call clean() here
        # Now, let's check if feedback is cleared
        self.assertEqual(lesson_status.feedback, "")  # Feedback should be cleared




