from django.test import TestCase
from tutorials.models import Status


class StatusTestCase(TestCase):
    """Test suite for the Status TextChoices enum."""

    def test_status_enum_values(self):
        """Test the values and names of the Status enum."""
        self.assertEqual(Status.PENDING, 'Pending')
        self.assertEqual(Status.BOOKED, 'Booked')
        self.assertEqual(Status.CANCELLED, 'Cancelled')
        self.assertEqual(Status.COMPLETED, 'Completed')

        self.assertEqual(Status.PENDING.label, 'Pending')
        self.assertEqual(Status.BOOKED.label, 'Booked')
        self.assertEqual(Status.CANCELLED.label, 'Cancelled')
        self.assertEqual(Status.COMPLETED.label, 'Completed')
