from django.test import TestCase
from tutorials.models import Lesson, LessonUpdateRequest, Tutor, Student, Subject, Term, User
from datetime import date, timedelta
from django.core.exceptions import ValidationError

class LessonUpdateRequestModelTestCase(TestCase):

    def setUp(self):
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
            subject=self.subject,
            term=self.term,
            frequency="W",
            duration=timedelta(hours=1),
            start_date=date.today(),
            price_per_lesson=50,
            notes="Test lesson"
        )

    def test_create_lesson_update_request(self):
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
            update_request.update_option,
            LessonUpdateRequest.UpdateOption.CHANGE_DAY_TIME
        )

    def test_default_values(self):
        update_request = LessonUpdateRequest.objects.create(lesson=self.lesson)
        self.assertEqual(update_request.update_option, "1")  # Default: Change Tutor
        self.assertEqual(update_request.details, "")
        self.assertEqual(update_request.made_by, "Tutor")
        self.assertEqual(update_request.is_handled, "N")  # Default: Not done

    def test_invalid_update_option(self):
        with self.assertRaises(ValidationError):
            lesson_update_request = LessonUpdateRequest.objects.create(
                lesson=self.lesson,
                update_option="InvalidOption"
            )
            lesson_update_request.full_clean()

    def test_invalid_made_by(self):
        with self.assertRaises(ValidationError):
            lesson_update_request = LessonUpdateRequest.objects.create(
                lesson=self.lesson,
                made_by="InvalidMadeBy"
            )
            lesson_update_request.full_clean()

    def test_invalid_is_handled(self):
        with self.assertRaises(ValidationError):
            lesson_update_request = LessonUpdateRequest(
                lesson=self.lesson,
                is_handled="InvalidIsHandled"
            )
            lesson_update_request.full_clean()

    def test_update_handled_status(self):
        update_request = LessonUpdateRequest.objects.create(lesson=self.lesson)
        update_request.is_handled = "Y"  # Mark as done
        update_request.save()
        self.assertEqual(update_request.is_handled, "Y")

    def test_str_representation(self):
        update_request = LessonUpdateRequest.objects.create(
            lesson=self.lesson,
            update_option="3"
        )
        self.assertEqual(
            update_request.update_option,
            LessonUpdateRequest.UpdateOption.CANCEL_LESSONS
        )
