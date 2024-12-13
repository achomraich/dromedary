from django.test import TestCase
from tutorials.forms import LessonFeedbackForm
from django import forms
from tutorials.models import LessonStatus, Lesson, User, Student, Status, Tutor, Term, Subject

from datetime import date, time, timedelta
import datetime

class LessonFeedbackFormTestCase(TestCase):

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
        self.form_data = {'feedback': 'This lesson was great!'}

        self.tutor = Tutor.objects.get(user__username='@petrapickles')
        self.student = Student.objects.get(user__username='@rogersmith')
        self.subject = Subject.objects.get(name='Python')
        self.term = Term.objects.get(start_date='2024-01-01')

        self.lesson = Lesson.objects.create(tutor=self.tutor,
                                            student=self.student,
                                            subject=self.subject,
                                            term=self.term,
                                            frequency='W',
                                            duration=datetime.timedelta(hours=2, minutes=30),
                                            start_date=datetime.date(2024, 9, 1),
                                            price_per_lesson=20)

        self.lesson_status = LessonStatus.objects.create(
            lesson_id=self.lesson,
            date=date(2024, 2, 10),
            time=time(12, 30),
            status=Status.COMPLETED,
            feedback="Great session",
            invoiced=True,
        )



    def test_valid_feedback_form(self):
        form = LessonFeedbackForm(data=self.form_data, instance=self.lesson_status)
        self.assertTrue(form.is_valid(), f"Form is invalid: {form.errors}")
        updated_status = form.save()
        self.assertEqual(updated_status.feedback, 'This lesson was great!')

    def test_existing_feedback_added_correctly(self):
        form = LessonFeedbackForm(data=self.form_data, instance=self.lesson_status)
        updated_status = form.save()
        self.assertEqual(updated_status.feedback, 'This lesson was great!')

    '''def test_existing_feedback_updated_correctly(self):
        self.form_data['feedback'] = "Old feedback"
        form = LessonFeedbackForm(data=self.form_data, instance=self.lesson_status)
        form.save()
        self.assertEqual(self.lesson_status.feedback, 'Old feedback')

        self.form_data['feedback'] = "New feedback"
        form = LessonFeedbackForm(data=self.form_data, instance=self.lesson_status)
        form.save()
        self.assertEqual(self.lesson_status.feedback, 'New feedback')'''

    def test_for_has_necessary_fields(self):

        form = LessonFeedbackForm()
        self.assertIn('lesson_name', form.fields)
        self.assertIn('student_name', form.fields)
        self.assertIn('lesson_date', form.fields)
        self.assertIn('lesson_time', form.fields)
        self.assertIn('feedback', form.fields)

        lesson_name_field = form.fields['lesson_name']
        student_name_field = form.fields['student_name']
        lesson_date_field = form.fields['lesson_date']
        lesson_time_field = form.fields['lesson_time']
        feedback_field = form.fields['feedback']
        self.assertTrue(isinstance(lesson_name_field, forms.CharField))
        self.assertTrue(isinstance(student_name_field, forms.CharField))
        self.assertTrue(isinstance(lesson_date_field, forms.DateField))
        self.assertTrue(isinstance(lesson_time_field, forms.TimeField))
        self.assertTrue(isinstance(feedback_field, forms.CharField))

    def test_lesson_exist(self):
        form = LessonFeedbackForm(data=self.form_data)
        self.assertFalse(form.is_valid())

    def test_initial_values(self):
        form = LessonFeedbackForm(instance=self.lesson_status)
        self.assertEqual(form.initial['lesson_name'], self.lesson.subject.name)
        self.assertEqual(form.initial['student_name'], self.student.user.full_name())
        self.assertEqual(form.initial['lesson_date'], self.lesson_status.date)
        self.assertEqual(form.initial['lesson_time'], self.lesson_status.time)

    def test_feedback_max_length(self):
        long_feedback = 'x' * 256
        self.form_data['feedback'] = long_feedback
        form = LessonFeedbackForm(data=self.form_data, instance=self.lesson_status)
        self.assertFalse(form.is_valid())

    def test_empty_form_data(self):
        form = LessonFeedbackForm(data={})
        self.assertFalse(form.is_valid())

    def test_feedback_field_is_editable(self):
        form = LessonFeedbackForm(data=self.form_data, instance=self.lesson_status)
        self.assertTrue(form.fields['lesson_name'].disabled)
        self.assertTrue(form.fields['student_name'].disabled)
        self.assertTrue(form.fields['lesson_date'].disabled)
        self.assertTrue(form.fields['lesson_time'].disabled)
        self.assertFalse(form.fields['feedback'].disabled)
