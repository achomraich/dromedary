from django.test import TestCase
from tutorials.forms import SubjectForm
from django import forms
from tutorials.models import Subject

class SubjectFormTestCase(TestCase):

    def setUp(self):
        self.form_input = {
            'name': 'C++',
            'description': 'Description of C++ course'
        }

        self.existing_subject = Subject.objects.create(name="Python", description="This is Python coding course")

    def test_valid_subject_form(self):
        form = SubjectForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_for_has_necessary_fields(self):
        form = SubjectForm()
        self.assertIn('name', form.fields)
        self.assertIn('description', form.fields)

        name_field = form.fields['name']
        description_field = form.fields['description']
        self.assertTrue(isinstance(name_field, forms.CharField))
        self.assertTrue(isinstance(description_field, forms.CharField))

    def test_blank_subject_name_is_invalid(self):
        self.form_input['name'] = ""
        form = SubjectForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_blank_subject_description_is_invalid(self):
        self.form_input['description'] = ""
        form = SubjectForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_overload_subject_name(self):
        self.form_input['name'] = "C++" * 7
        form = SubjectForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_overload_subject_descripton(self):
        self.form_input['description'] = "-" * 256
        form = SubjectForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_valid_form_can_be_saved(self):
        form = SubjectForm(data=self.form_input)
        before_count = Subject.objects.count()
        form.save()
        after_count = Subject.objects.count()
        self.assertEqual(before_count, after_count-1)

    def test_existing_subject_updated_correctly(self):
        form = SubjectForm(data=self.form_input, instance=self.existing_subject)
        before_count = Subject.objects.count()
        updated_status = form.save()
        after_count = Subject.objects.count()
        self.assertEqual(before_count, after_count)
        self.assertEqual(updated_status.description, 'Description of C++ course')
        self.assertEqual(updated_status.name, 'Python')

    def test_existing_subject_is_not_updated_correctly(self):
        self.form_input['description'] = ''
        form = SubjectForm(data=self.form_input, instance=self.existing_subject)
        self.assertFalse(form.is_valid())

    def test_form_disables_name_for_existing_subject(self):
        form = SubjectForm(instance=self.existing_subject)
        self.assertTrue(form.fields['name'].disabled)

    def test_form_enables_name_for_new_subject(self):
        form = SubjectForm()
        self.assertFalse(form.fields['name'].disabled)

    def test_form_handles_none_instance(self):
        form = SubjectForm(instance=None)
        self.assertFalse(form.fields['name'].disabled)