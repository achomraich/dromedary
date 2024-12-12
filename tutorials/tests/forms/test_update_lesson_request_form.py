from django.test import TestCase
from tutorials.forms import UpdateLessonRequestForm, UpdateLessonForm
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
                                        end_date=datetime.date(2025, 1, 15))

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
            date=datetime.date(2024, 9, 1),
            time=datetime.time(20, 15),
            status=Status.SCHEDULED,
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
            LessonUpdateRequest.UpdateOption.choices,
            "update_option should display all default choices when no user role is provided."
        )
        self.assertTrue(isinstance(details_field, forms.CharField))

    def test_blank_update_option_is_invalid(self):
        self.form_data['update_option'] = ""
        form = UpdateLessonRequestForm(data=self.form_data, instance=self.lesson_update_request, user_role=self.user_role)
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

    def test_update_lesson_request_form_tutor_role(self):
        """Test the form for a tutor role."""
        form = UpdateLessonRequestForm(instance=self.lesson_update_request, user_role=self.tutor.user)

        # Check that the 'tutor_name' is correctly populated for a tutor
        self.assertEqual(form.initial['tutor_name'], self.lesson.student.user.get_full_name())

        # Ensure that the 'duration' and 'frequency' fields are populated
        self.assertEqual(form.initial['duration'], self.lesson.duration)
        self.assertEqual(form.initial['frequency'], self.lesson.frequency)

        # Check that the 'update_option' field contains only relevant choices for tutor
        self.assertIn(('1', 'Change Tutor'), form.fields['update_option'].choices)
        self.assertIn(('2', 'Change Day/Time'), form.fields['update_option'].choices)
        self.assertNotIn(('3', 'Cancel Lessons'), form.fields['update_option'].choices)

    def test_update_lesson_request_form_student_role(self):
        """Test the form for a student role."""
        form = UpdateLessonRequestForm(instance=self.lesson_update_request, user_role=self.student.user)

        # Check that the 'tutor_name' is correctly populated for a student
        self.assertEqual(form.initial['tutor_name'], self.lesson.tutor.user.get_full_name())

        # Ensure that 'duration' and 'frequency' are populated
        self.assertEqual(form.initial['duration'], self.lesson.duration)
        self.assertEqual(form.initial['frequency'], self.lesson.frequency)

        # Check that the 'update_option' field contains only relevant choices for student
        self.assertIn(('2', 'Change Day/Time'), form.fields['update_option'].choices)
        self.assertIn(('3', 'Cancel Lessons'), form.fields['update_option'].choices)

    def test_update_lesson_form_initialization(self):
        form = UpdateLessonForm(instance=self.lesson,
                                update_option='2',
                                details="Test details",
                                day_of_week=0,
                                regular_lesson_time=self.lesson.set_start_time,
                                next_lesson_date='2024-12-30')

        self.assertEqual(form.initial['details'], "Test details")
        self.assertEqual(form.initial['subject'], self.lesson.subject.name)
        self.assertEqual(form.initial['duration'], str(self.lesson.duration))
        self.assertEqual(form.initial['frequency'], 'Weekly')
        self.assertEqual(form.initial['lesson_time'], self.lesson.set_start_time)

        # Check the disabled fields
        self.assertTrue(form.fields['tutor'].disabled)
        self.assertTrue(form.fields['student'].disabled)

    def test_form_new_tutor_queryset_based_on_subject(self):
        form = UpdateLessonForm(instance=self.lesson,
                                update_option='2',
                                details="Test details",
                                day_of_week=0,
                                regular_lesson_time=self.lesson.set_start_time,
                                next_lesson_date='2024-12-30')

        self.tutor.subjects.set([self.subject])

        self.assertTrue(form.fields['new_tutor'].queryset.filter(subjects=self.subject).exists())

    def test_form_invalid_data(self):
        """Test that form raises validation errors with invalid data."""
        form_data = {
            'new_tutor': Tutor.objects.get(pk=1),  # Missing new tutor, for example
            'new_lesson_time': '10:00:00',
            'new_day_of_week': '2024-12-12',  # Invalid date format
        }



        form = UpdateLessonForm(instance=self.lesson,
                                data=form_data, update_option='1',
                                day_of_week=0,)

        # Check if form is not valid due to missing required fields or incorrect formats
        self.assertFalse(form.is_valid())
        self.assertIn('new_tutor', form.errors)

    def test_update_lesson_request_form_save(self):
        """Test saving the form and making sure initial data is correctly passed."""
        data = {
            'update_option': 2,
            'details': "Test details"
        }
        form = UpdateLessonRequestForm(instance=self.lesson_update_request, user_role=self.student, data=data)
        self.assertTrue(form.is_valid())
        updated_instance = form.save()

        # Verify that the lesson update request instance was saved correctly
        self.assertEqual(updated_instance.details, "Test details")
        self.assertEqual(updated_instance.update_option, "2")
