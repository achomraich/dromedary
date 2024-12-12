from django.test import TestCase
from tutorials.models import Lesson, Tutor, Student, Subject, Term, User
from datetime import date, timedelta
from django.core.exceptions import ValidationError

class LessonModelTestCase(TestCase):

    def setUp(self):
        self.tutor = Tutor.objects.create(
            user=User.objects.create(username="@tutor1", first_name="John", last_name="Doe", email="tutor1@example.com")
        )
        self.student = Student.objects.create(
            user=User.objects.create(username="@student1", first_name="Jane", last_name="Doe", email="student1@example.com")
        )
        self.subject = Subject.objects.create(name="Python", description="Python Subject")
        self.term = Term.objects.create(start_date=date(2024, 9, 1), end_date=date(2025, 1, 31))

        self.lesson = Lesson.objects.create(
            tutor=self.tutor,
            student=self.student,
            subject_id=self.subject,
            term_id=self.term,
            frequency="W",
            duration=timedelta(hours=1, minutes=30),
            start_date=date(2024, 9, 15),
            price_per_lesson=50,
        )

    def test_create_valid_lesson(self):

        self.assertEqual(self.lesson.tutor, self.tutor)
        self.assertEqual(self.lesson.frequency, "W")
        self.assertEqual(self.lesson.notes, "—")  # Default value

    def test_valid_lesson_is_valid(self):
        try:
            self.lesson.full_clean()
        except ValidationError:
            self.fail("Default test student should be deemed valid!")

    def test_invalid_frequency_choice(self):
        with self.assertRaises(ValidationError):
            lesson = Lesson(
                tutor=self.tutor,
                student=self.student,
                subject_id=self.subject,
                term_id=self.term,
                frequency="INVALID",  # Invalid choice
                duration=timedelta(hours=1, minutes=30),
                start_date=date(2023, 9, 15),
                price_per_lesson=50,
            )
            lesson.full_clean()

    def test_missing_required_fields(self):
        with self.assertRaises(ValidationError):
            lesson = Lesson(
                tutor=self.tutor,
                # Missing student
                subject_id=self.subject,
                term_id=self.term,
                frequency="W",
                duration=timedelta(hours=1, minutes=30),
                start_date=date(2023, 9, 15),
                price_per_lesson=50,
            )
            lesson.full_clean()  # Trigger validation

    def test_negative_price_per_lesson(self):
        with self.assertRaises(ValidationError):
            lesson = Lesson(
                tutor=self.tutor,
                student=self.student,
                subject_id=self.subject,
                term_id=self.term,
                frequency="W",
                duration=timedelta(hours=1, minutes=30),
                start_date=date(2023, 9, 15),
                price_per_lesson=-10,  # Negative price
            )
            lesson.full_clean()

    def test_lesson_duration(self):
        lesson = Lesson.objects.create(
            tutor=self.tutor,
            student=self.student,
            subject_id=self.subject,
            term_id=self.term,
            frequency="W",
            duration=timedelta(hours=2),
            start_date=date(2023, 9, 15),
            price_per_lesson=100,
        )
        self.assertEqual(lesson.duration, timedelta(hours=2))

        with self.assertRaises(ValidationError):
            lesson = Lesson(
                tutor=self.tutor,
                student=self.student,
                subject_id=self.subject,
                term_id=self.term,
                frequency="W",
                duration=timedelta(hours=-1),
                start_date=date(2023, 9, 15),
                price_per_lesson=50,
            )
            lesson.full_clean()

        with self.assertRaises(ValidationError):
            lesson = Lesson(
                tutor=self.tutor,
                student=self.student,
                subject_id=self.subject,
                term_id=self.term,
                frequency="W",
                duration="timedelta(hours=-1)",
                start_date=date(2023, 9, 15),
                price_per_lesson=50,
            )
            lesson.full_clean()

    def test_default_notes_value(self):
        lesson = Lesson.objects.create(
            tutor=self.tutor,
            student=self.student,
            subject_id=self.subject,
            term_id=self.term,
            frequency="W",
            duration=timedelta(hours=1),
            start_date=date(2023, 9, 15),
            price_per_lesson=50,
        )
        self.assertEqual(lesson.notes, "—")
