from django.test import TestCase
from tutorials.forms import LessonFeedbackForm
from django import forms
from tutorials.models.models import LessonStatus, Lesson, User, Student, Status, Tutor, Term, Subject
import datetime

class LessonFeedbackFormTestCase(TestCase):

    def setUp(self):
        self.form_data = {'feedback': 'This lesson was great!'}

        self.user1 = User.objects.create_user(first_name="Jane",
                                             last_name="Doe",
                                             username="@janedoe",
                                             email="janedoe@example.org")

        self.user2 = User.objects.create_user(first_name="Charlie",
                                             last_name="Johnson",
                                             username="@charlie",
                                             email="charlie.johnson@example.org")
        self.user1.set_password('Password123')
        self.user2.set_password('Password123')

        self.tutor = Tutor.objects.create(user=self.user1)
        self.student = Student.objects.create(user=self.user2)

        self.subject = Subject.objects.create(name="Python", description="This is Python coding course")

        self.term = Term.objects.create(start_date=datetime.date(2024, 9, 1),
                                        end_date=datetime.date(2025, 1, 15))

        self.lesson = Lesson.objects.create(tutor=self.tutor,
                                            student=self.student,
                                            subject_id=self.subject,
                                            term_id=self.term,
                                            frequency='D',
                                            duration=datetime.timedelta(hours=2, minutes=30),
                                            start_date=datetime.date(2024, 9, 1),
                                            price_per_lesson=20)

        self.lesson_status = LessonStatus.objects.create(
            lesson_id=self.lesson,
            date=datetime.date(2024, 9, 1),
            time=datetime.time(20, 15),
            status=Status.BOOKED,
            feedback="",
            invoiced=False
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

    def test_existing_feedback_updated_correctly(self):
        self.form_data['feedback'] = "Old feedback"
        form = LessonFeedbackForm(data=self.form_data, instance=self.lesson_status)
        form.save()
        self.assertEqual(self.lesson_status.feedback, 'Old feedback')

        self.form_data['feedback'] = "New feedback"
        form = LessonFeedbackForm(data=self.form_data, instance=self.lesson_status)
        form.save()
        self.assertEqual(self.lesson_status.feedback, 'New feedback')

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
        self.assertEqual(form.initial['lesson_name'], self.lesson.subject_id.name)
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

