from django.test import TestCase
from tutorials.forms import TutorAvailabilityForm, TutorAvailabilityList
from tutorials.models import Tutor, User


class TutorAvailabilityFormTests(TestCase):

    def setUp(self):
        # Create a test user and tutor for the current_tutor parameter
        self.user = User.objects.create_user(username="testuser", first_name="Test", last_name="User")
        self.tutor = Tutor.objects.create(user=self.user)

    def test_dynamic_choices_for_day_and_status(self):
        """Test that the 'day' and 'status' fields have dynamic choices."""
        form = TutorAvailabilityForm()

        # Check the dynamic choices for 'day'
        day_choices = form.fields['day'].choices
        self.assertIn(('', 'Select an option'), day_choices)
        self.assertTrue(all(choice[0] != '' for choice in day_choices[1:]))

        # Check the dynamic choices for 'status'
        status_choices = form.fields['status'].choices
        self.assertIn(('', 'Select an option'), status_choices)
        self.assertTrue(all(choice[0] != '' for choice in status_choices[1:]))

    def test_current_tutor_field_in_form(self):
        """Test that the 'current_tutor_name' field is added when a current_tutor is provided."""
        # Pass the current_tutor parameter to the form
        form = TutorAvailabilityList(current_tutor=self.tutor)

        # Check if 'current_tutor_name' field is added
        self.assertIn('current_tutor_name', form.fields)
        self.assertEqual(
            form.fields['current_tutor_name'].initial,
            self.tutor.user.get_full_name()  # Ensure it matches the tutor's full name
        )

        # Check that the field is disabled and readonly
        self.assertTrue(form.fields['current_tutor_name'].disabled)
        self.assertIn('readonly', form.fields['current_tutor_name'].widget.attrs)

    def test_form_initialization(self):
        """Test that the form initializes correctly with and without 'current_tutor'."""
        # Test initialization of TutorAvailabilityForm without current_tutor
        form = TutorAvailabilityForm()
        self.assertIsNotNone(form)

        # Test initialization of TutorAvailabilityList without current_tutor
        form_without_tutor = TutorAvailabilityList()
        self.assertIsNotNone(form_without_tutor)

        # Test initialization of TutorAvailabilityList with current_tutor
        form_with_tutor = TutorAvailabilityList(current_tutor=self.tutor)
        self.assertIsNotNone(form_with_tutor)
