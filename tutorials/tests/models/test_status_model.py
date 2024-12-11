from django.test import TestCase
from tutorials.models.models import Status


class StatusTestCase(TestCase):

    def test_status_enum_values(self):
        self.assertEqual(Status.PENDING, 'Pending')
        self.assertEqual(Status.BOOKED, 'Booked')
        self.assertEqual(Status.CANCELLED, 'Cancelled')
        self.assertEqual(Status.COMPLETED, 'Completed')

        self.assertEqual(Status.PENDING.label, 'Pending')
        self.assertEqual(Status.BOOKED.label, 'Booked')
        self.assertEqual(Status.CANCELLED.label, 'Cancelled')
        self.assertEqual(Status.COMPLETED.label, 'Completed')
