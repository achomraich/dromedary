from django.test import TestCase
from tutorials.models import Term
from datetime import date
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError


class TermModelTestCase(TestCase):
    """Test suite for the Term model."""

    def setUp(self):
        """Set up initial data for testing."""
        self.term = Term.objects.create(
            start_date=date(2023, 9, 1),
            end_date=date(2024, 1, 31)
        )

    def test_valid_tutor_is_valid(self):
        try:
            self.term.full_clean()
        except ValidationError:
            self.fail("Default test term should be deemed valid!")

    def test_create_term(self):
        """Ensure that we can create a term with a start and end date."""
        start_date = date(2024, 9, 1)
        end_date = date(2025, 1, 31)
        term = Term.objects.create(start_date=start_date, end_date=end_date)

        self.assertEqual(term.start_date, start_date)
        self.assertEqual(term.end_date, end_date)

    def test_invalid_term_end_date(self):
        """Ensure that the end date is not before the start date."""
        start_date = date(2024, 1, 31)
        end_date = date(2023, 12, 31)

        with self.assertRaises(ValidationError):
            Term.objects.create(start_date=start_date, end_date=end_date)

    def test_same_start_and_end_date(self):
        """Ensure that the start date and end date are not the same."""
        start_date = date(2024, 1, 1)
        end_date = date(2024, 1, 1)

        with self.assertRaises(ValidationError):
            Term.objects.create(start_date=start_date, end_date=end_date)
