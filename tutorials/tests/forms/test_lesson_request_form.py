from django.test import TestCase
from django.core.exceptions import ValidationError
from datetime import timedelta, date, time
from tutorials.models import LessonRequest, Student, Subject, Term, Frequency, Status, Tutor, Lesson

class LessonRequestTest(TestCase):

    fixtures = [
        'tutorials/tests/fixtures/default_user.json',
        'tutorials/tests/fixtures/other_users.json',
        'tutorials/tests/fixtures/default_subject.json',
        'tutorials/tests/fixtures/default_tutor.json',
        'tutorials/tests/fixtures/default_term.json',
        'tutorials/tests/fixtures/default_student.json',
    ]

    def setUp(self):
        # Set up a term

        self.tutor = Tutor.objects.get(user__username='@petrapickles')
        self.student = Student.objects.get(user__username='@rogersmith')
        self.subject = Subject.objects.get(name='Python')
        self.term = Term.objects.get(start_date='2024-09-01')

        self.valid_data = {
            'student': self.student,
            'subject': self.subject,
            'term': self.term,
            'time': time(10, 0),
            'start_date': '2024-12-25',
            'frequency': Frequency.WEEKLY,
            'duration': timedelta(hours=1)
        }

    def test_valid_lesson_request(self):
        """Test that a valid LessonRequest passes validation."""
        self.valid_data["start_date"] = date.today() + timedelta(days=10)
        lesson_request = LessonRequest(**self.valid_data)
        try:
            lesson_request.clean()
        except ValidationError:
            self.fail("clean() raised ValidationError unexpectedly for valid data!")

    def test_start_date_in_future(self):
        """Test that a start date in the past raises a ValidationError."""
        self.valid_data['start_date'] = date.today() - timedelta(days=1)
        lesson_request = LessonRequest(**self.valid_data)
        with self.assertRaises(ValidationError) as e:
            lesson_request.clean()
        self.assertIn("Start date must be in the future.", str(e.exception))

    def test_start_date_within_term(self):
        # Test start date before term
        self.valid_data["start_date"] = self.term.start_date + timedelta(days=200)
        lesson_request = LessonRequest(**self.valid_data)
        with self.assertRaises(ValidationError) as e:
            lesson_request.clean()
        self.assertIn("Start date must be within the term.", str(e.exception))


    def test_positive_duration(self):
        self.valid_data['duration'] = timedelta(0)
        lesson_request = LessonRequest(**self.valid_data)
        with self.assertRaises(ValidationError) as e:
            lesson_request.clean()
        self.assertIn("Duration must be a positive value.", str(e.exception))

        self.valid_data['duration'] = timedelta(hours=-1)
        lesson_request = LessonRequest(**self.valid_data)
        with self.assertRaises(ValidationError) as e:
            lesson_request.clean()
        self.assertIn("Duration must be a positive value.", str(e.exception))

    def test_decided_status(self):
        lesson_request = LessonRequest.objects.create(**self.valid_data)
        lesson_request.status = Status.PENDING
        self.assertFalse(lesson_request.decided())

        lesson_request.status = Status.CONFIRMED
        self.assertTrue(lesson_request.decided())

        lesson_request.status = Status.CANCELLED
        self.assertTrue(lesson_request.decided())

    def test_cancelled_status(self):
        lesson_request = LessonRequest.objects.create(**self.valid_data)
        lesson_request.status = Status.CANCELLED
        self.assertTrue(lesson_request.cancelled())

        lesson_request.status = Status.CONFIRMED
        self.assertFalse(lesson_request.cancelled())

    def test_confirmed_status(self):
        lesson_request = LessonRequest.objects.create(**self.valid_data)
        lesson_request.status = Status.CONFIRMED
        self.assertTrue(lesson_request.confirmed())

        lesson_request.status = Status.CANCELLED
        self.assertFalse(lesson_request.confirmed())

    def test_lesson_assignment(self):

        lesson = Lesson.objects.create(
            tutor=self.tutor,
            student=self.student,
            subject=self.subject,
            term=self.term,
            frequency=Frequency.BIWEEKLY,
            set_start_time=time(10, 0),
            start_date=self.term.start_date,
            price_per_lesson=50.00
        )

        lesson_request = LessonRequest.objects.create(**self.valid_data)
        lesson_request.lesson_assigned = lesson
        lesson_request.save()
        self.assertEqual(lesson_request.lesson_assigned, lesson)

    def test_positive_duration(self):
        self.valid_data["duration"] = timedelta(0)
        lesson_request = LessonRequest(**self.valid_data)
        with self.assertRaises(ValidationError) as e:
            lesson_request.clean()
        self.assertIn("Duration must be a positive value.", str(e.exception))
