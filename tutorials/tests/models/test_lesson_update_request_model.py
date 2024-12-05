from django.test import TestCase
from tutorials.models import Lesson, LessonUpdateRequest, Tutor, Student, Subject, Term, User
from datetime import date, timedelta
from django.core.exceptions import ValidationError

class LessonUpdateRequestModelTestCase(TestCase):
    """Test cases for the LessonUpdateRequest model."""

    def setUp(self):
        """Set up required objects for the tests."""
        # Create required related objects
        self.tutor = Tutor.objects.create(user=User.objects.create(username="tutor1", email="tutor1@example.com"))
        self.student = Student.objects.create(
            user=User.objects.create(username="student1", email="student1@example.com"))
        self.subject = Subject.objects.create(name="Python", description="Test Subject")
        self.term = Term.objects.create(
            start_date=date.today() - timedelta(days=30),
            end_date=date.today() + timedelta(days=30)
        )
        self.lesson = Lesson.objects.create(
            tutor=self.tutor,
            student=self.student,
            subject_id=self.subject,
            term_id=self.term,
            frequency="W",
            duration=timedelta(hours=1),
            start_date=date.today(),
            price_per_lesson=50,
            notes="Test lesson"
        )

    def test_create_lesson_update_request(self):
        """Test creating a valid LessonUpdateRequest."""
        update_request = LessonUpdateRequest.objects.create(
            lesson=self.lesson,
            update_option="2",
            details="Change lesson time to 3 PM",
            made_by="Student",
            is_handled="N"
        )
        self.assertEqual(update_request.lesson, self.lesson)
        self.assertEqual(update_request.update_option, "2")
        self.assertEqual(update_request.details, "Change lesson time to 3 PM")
        self.assertEqual(update_request.made_by, "Student")
        self.assertEqual(update_request.is_handled, "N")
        self.assertEqual(
            str(update_request),
            f"Update Request for Lesson {self.lesson.lesson_id} - Change Day/Time"
        )

    def test_default_values(self):
        """Test default values for the LessonUpdateRequest model."""
        update_request = LessonUpdateRequest.objects.create(lesson=self.lesson)
        self.assertEqual(update_request.update_option, "1")  # Default: Change Tutor
        self.assertEqual(update_request.details, "")
        self.assertEqual(update_request.made_by, "Tutor")
        self.assertEqual(update_request.is_handled, "N")  # Default: Not done

    def test_invalid_update_option(self):
        """Test that invalid update_option raises an error."""
        with self.assertRaises(ValidationError):
            lesson_update_request = LessonUpdateRequest.objects.create(
                lesson=self.lesson,
                update_option="InvalidOption"
            )
            lesson_update_request.full_clean()

    def test_invalid_made_by(self):
        """Test that invalid made_by raises an error."""
        with self.assertRaises(ValidationError):
            lesson_update_request = LessonUpdateRequest.objects.create(
                lesson=self.lesson,
                made_by="InvalidMadeBy"
            )
            lesson_update_request.full_clean()

    def test_invalid_is_handled(self):
        """Test that invalid is_handled raises an error."""
        with self.assertRaises(ValidationError):
            lesson_update_request = LessonUpdateRequest(
                lesson=self.lesson,
                is_handled="InvalidIsHandled"
            )
            lesson_update_request.full_clean()

    def test_update_handled_status(self):
        """Test updating the is_handled field."""
        update_request = LessonUpdateRequest.objects.create(lesson=self.lesson)
        update_request.is_handled = "Y"  # Mark as done
        update_request.save()
        self.assertEqual(update_request.is_handled, "Y")

    def test_str_representation(self):
        """Test the string representation of the model."""
        update_request = LessonUpdateRequest.objects.create(
            lesson=self.lesson,
            update_option="3"
        )
        self.assertEqual(
            str(update_request),
            f"Update Request for Lesson {self.lesson.lesson_id} - Cancel Lessons"
        )
