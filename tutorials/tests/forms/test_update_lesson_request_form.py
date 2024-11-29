from django.test import TestCase
from tutorials.forms import UpdateLessonRequestForm
from django import forms
from tutorials.models import LessonStatus, Lesson, User, Student, Status, Tutor, Term, Subject, LessonUpdateRequest
import datetime


class LessonUpdateRequestTestCase(TestCase):

    def setUp(self):

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
                                        end_date=datetime.date(2024, 1, 15))

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

        self.form_data = {'update_option': '2',
                          'details': 'xxx'}

        self.lesson_update_request = LessonUpdateRequest.objects.create(
            lesson=self.lesson,
            made_by='Tutor'
        )

        self.user_role = self.user1

    def test_valid_request_form(self):
        form = UpdateLessonRequestForm(data=self.form_data, instance=self.lesson_update_request, user_role=self.user_role)
        self.assertTrue(form.is_valid())

    def test_invalid_tutor_request_form(self):
        self.form_data['update_option'] = '1'
        form = UpdateLessonRequestForm(data=self.form_data, instance=self.lesson_update_request, user_role=self.user_role)
        self.assertFalse(form.is_valid(), f"Form is invalid: Tutor can't change itself")

    def test_for_has_necessary_fields(self):
        form = UpdateLessonRequestForm()
        self.assertIn('tutor_name', form.fields)
        self.assertIn('duration', form.fields)
        self.assertIn('frequency', form.fields)
        self.assertIn('update_option', form.fields)
        self.assertIn('details', form.fields)

        tutor_name_field = form.fields['tutor_name']
        duration_field = form.fields['duration']
        frequency_field = form.fields['frequency']
        details_field = form.fields['details']
        self.assertTrue(isinstance(tutor_name_field, forms.CharField))
        self.assertTrue(isinstance(duration_field, forms.CharField))
        self.assertTrue(isinstance(frequency_field, forms.CharField))
        self.assertEqual(
            type(details_field.widget),
            forms.Textarea
        )
        update_option_choices = form.fields['update_option'].choices
        self.assertEqual(
            update_option_choices,
            LessonUpdateRequest.UPDATE_CHOICES,
            "update_option should display all default choices when no user role is provided."
        )
        self.assertTrue(isinstance(details_field, forms.CharField))

    def test_blank_update_option_is_invalid(self):
        self.form_data['update_option'] = ""
        form = UpdateLessonRequestForm(data=self.form_data, instance=self.lesson_update_request, user_role=self.user_role)
        self.assertFalse(form.is_valid())

    def test_blank_details_field_is_invalid(self):
        self.form_data['details'] = ""
        form = UpdateLessonRequestForm(data=self.form_data, instance=self.lesson_update_request,
                                       user_role=self.user_role)
        self.assertFalse(form.is_valid())

    def test_feedback_field_is_editable(self):
        form = UpdateLessonRequestForm(data=self.form_data, instance=self.lesson_update_request,
                                       user_role=self.user_role)
        self.assertTrue(form.fields['tutor_name'].disabled)
        self.assertTrue(form.fields['duration'].disabled)
        self.assertTrue(form.fields['frequency'].disabled)
        self.assertFalse(form.fields['update_option'].disabled)
        self.assertFalse(form.fields['details'].disabled)

    def test_empty_form_data(self):
        form = UpdateLessonRequestForm(data={})
        self.assertFalse(form.is_valid())

    def test_details_max_length(self):
        long_details_field = 'x' * 256
        self.form_data['details'] = long_details_field
        form = UpdateLessonRequestForm(data=self.form_data, instance=self.lesson_update_request,
                                       user_role=self.user_role)
        self.assertFalse(form.is_valid())

    def test_initial_values(self):
        form = UpdateLessonRequestForm(data=self.form_data, instance=self.lesson_update_request,
                                       user_role=self.user_role)

        self.assertEqual(form.initial['tutor_name'], self.lesson.student.user.full_name())
        self.assertEqual(form.initial['duration'], self.lesson.duration)
        self.assertEqual(form.initial['frequency'], self.lesson.frequency)

    def test_request_added_correctly(self):
        form = UpdateLessonRequestForm(data=self.form_data, instance=self.lesson_update_request,
                                       user_role=self.user_role)

        before_count = LessonUpdateRequest.objects.count()
        form.is_valid()
        updated_request = form.save()
        after_count = LessonUpdateRequest.objects.count()

        self.assertEqual(before_count, after_count)
        self.assertEqual(updated_request.update_option, '2')
        self.assertEqual(updated_request.details, 'xxx')

    def test_initial_values_with_student_profile(self):
        self.user_role = self.user2
        form = UpdateLessonRequestForm(data=self.form_data, instance=self.lesson_update_request,
                                       user_role=self.user_role)
        self.assertEqual(form.initial['tutor_name'], self.lesson.tutor.user.full_name())
