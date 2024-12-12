"""Unit tests of the tutor assigning form."""
import datetime

from django.test import TestCase
from tutorials.forms import AssignTutorForm
from tutorials.models import Lesson, Tutor, Subject, Term, Student, LessonRequest

class AssignTutorFormTestCase(TestCase):
    """Unit tests of the tutor assigning form."""

    fixtures = [
        'tutorials/tests/fixtures/default_user.json',
        'tutorials/tests/fixtures/other_users.json',
        'tutorials/tests/fixtures/default_subject.json',
        'tutorials/tests/fixtures/default_tutor.json',
        'tutorials/tests/fixtures/default_term.json',
        'tutorials/tests/fixtures/default_student.json',
        'tutorials/tests/fixtures/default_lesson.json',
    ]

    def setUp(self):
        self.tutor = Tutor.objects.get(user__username='@petrapickles')
        self.student = Student.objects.get(user__username='@rogersmith')
        self.subject = Subject.objects.get(name='Python')
        self.term = Term.objects.get(start_date='2024-01-01')
        self.existing_request = LessonRequest.objects.create(
            student=self.student,
            subject=self.subject,
            term=self.term,
            time=datetime.time(hour=15, minute=0, second=0),
            duration= datetime.timedelta(hours=1),
            frequency= 'B',
            start_date= '2024-01-01',
        )
        self.form_data = {
            'tutor': self.tutor,
            'subject_id': self.subject,
            'term_id': self.term,
            'student': self.student,
            'duration': '01:00:00',
            'frequency': 'B',
            'start_date': '2024-01-01',
            'price_per_lesson': 25
        }

    def test_form_initialization_without_existing_request(self):
        form = AssignTutorForm()
        self.assertIn('student', form.fields)
        self.assertFalse(form.fields['student'].disabled)

    def test_form_initialization_with_existing_request(self):
        # Initialize form with existing_request
        form = AssignTutorForm(existing_request=self.existing_request)

        # Check if fields are disabled and have correct initial values
        self.assertTrue(form.fields['student'].disabled)
        self.assertEqual(form.fields['student'].initial, self.existing_request.student)
        self.assertTrue(form.fields['subject_id'].disabled)
        self.assertEqual(form.fields['subject_id'].initial, self.existing_request.subject)
        self.assertTrue(form.fields['term_id'].disabled)
        self.assertEqual(form.fields['term_id'].initial, self.existing_request.term)
        self.assertTrue(form.fields['duration'].disabled)
        self.assertEqual(form.fields['duration'].initial, self.existing_request.duration)
        self.assertTrue(form.fields['frequency'].disabled)
        self.assertEqual(form.fields['frequency'].initial, self.existing_request.frequency)
        self.assertTrue(form.fields['start_date'].disabled)
        self.assertEqual(form.fields['start_date'].initial, self.existing_request.start_date)

    def test_form_valid_data(self):
        # Test form with valid data
        form = AssignTutorForm(data=self.form_data)
        self.assertTrue(form.is_valid())

    def test_form_invalid_data(self):
        # Test form with missing data
        invalid_data = self.form_data.copy()
        invalid_data['price_per_lesson'] = ''
        form = AssignTutorForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('price_per_lesson', form.errors)

    def test_form_saves_correctly(self):
        # Test that form saves data correctly
        form = AssignTutorForm(data=self.form_data)
        self.assertTrue(form.is_valid())
        lesson = form.save(commit=False)
        lesson.save()

        saved_lesson = Lesson.objects.last()
        self.assertEqual(saved_lesson.student, self.student)
        self.assertEqual(saved_lesson.tutor, self.tutor)
        self.assertEqual(saved_lesson.subject_id, self.subject)
        self.assertEqual(saved_lesson.term_id, self.term)
        self.assertEqual(saved_lesson.duration, datetime.timedelta(hours=1))
        self.assertEqual(saved_lesson.frequency, 'B')
        self.assertEqual(saved_lesson.start_date.strftime('%Y-%m-%d'), '2024-01-01')
        self.assertEqual(saved_lesson.price_per_lesson, 25.0)

    def test_field_customizations(self):
        # Test custom attributes and labels
        form = AssignTutorForm()
        self.assertEqual(form.fields['tutor'].widget.attrs['class'], 'form-select')
        self.assertEqual(form.fields['start_date'].widget.attrs['class'], 'form-control')
        self.assertEqual(form.fields['price_per_lesson'].widget.attrs['class'], 'form-control')
        self.assertEqual(form.fields['price_per_lesson'].widget.attrs['placeholder'], 'Enter price')
        self.assertEqual(form.fields['price_per_lesson'].label, 'Select a price per lesson ($)')