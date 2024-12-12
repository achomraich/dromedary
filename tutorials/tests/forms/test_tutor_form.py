"""Unit tests of the tutor form."""
from django import forms
from django.test import TestCase
from django.forms import ModelMultipleChoiceField
from tutorials.forms import TutorForm
from tutorials.models import Tutor, Subject, User

class UserFormTestCase(TestCase):
    """Unit tests of the tutor form."""

    fixtures = [
        'tutorials/tests/fixtures/default_user.json',
        'tutorials/tests/fixtures/other_users.json',
        'tutorials/tests/fixtures/default_tutor.json',
        'tutorials/tests/fixtures/default_subject.json'
    ]

    def setUp(self):
        self.tutor = Tutor.objects.get(user__username='@petrapickles')
        self.subject1 = Subject.objects.get(name='Python')
        self.subject2 = Subject.objects.get(name='C++')

        self.form_input = {
            'experience': 'I have 3 years of experience teaching Python',
            'subjects': [self.subject1.subject_id, self.subject2.subject_id],
        }

    def test_form_initialization_without_instance(self):
        # Initialize form without an instance
        form = TutorForm()
        self.assertIsInstance(form.fields['subjects'], ModelMultipleChoiceField)
        self.assertEqual(list(form.fields['subjects'].queryset), list(Subject.objects.all()))

    def test_form_initialization_with_instance(self):
        # Initialize form with a tutor instance
        form = TutorForm(instance=self.tutor)
        self.assertEqual(form.fields['subjects'].queryset.count(), 2)
        self.assertIn(self.subject1, form.fields['subjects'].queryset)
        self.assertIn(self.subject2, form.fields['subjects'].queryset)

    def test_form_has_necessary_fields(self):
        form = TutorForm()
        self.assertIn('subjects', form.fields)
        self.assertIn('experience', form.fields)

    def test_valid_user_form(self):
        form = TutorForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_uses_model_validation(self):
        self.form_input['subjects'] = ['Random']
        form = TutorForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_must_save_correctly(self):
        form = TutorForm(instance=self.tutor, data=self.form_input)
        self.assertTrue(form.is_valid())
        form.save()
        self.tutor.refresh_from_db()

        self.assertEqual(self.tutor.experience, 'I have 3 years of experience teaching Python')

        saved_subjects = list(self.tutor.subjects.values_list('subject_id', flat=True))
        self.assertEqual(saved_subjects, [self.subject1.subject_id, self.subject2.subject_id])

    def test_field_customizations(self):
        # Verify field customizations
        form = TutorForm()
        self.assertEqual(form.fields['experience'].widget.attrs['placeholder'],
                         'Tell us more about your experience in teaching...')
        self.assertEqual(form.fields['experience'].label, 'Experience')
        self.assertEqual(form.fields['subjects'].label, 'Subjects Taught')
        self.assertIsInstance(form.fields['subjects'].widget, forms.CheckboxSelectMultiple)
        self.assertEqual(form.fields['subjects'].widget.attrs['class'], 'form-check-inline')
