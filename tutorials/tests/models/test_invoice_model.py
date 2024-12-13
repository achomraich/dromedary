# DromeDary > tutorials folder > tests > models folder > test_invoice_model.py

from django.test import TestCase
from django.core.exceptions import ValidationError
from datetime import date, timedelta
from tutorials.models import (
    Invoice, Student, User, LessonStatus, Tutor,
    Subject, Term, Lesson, InvoiceLessonLink, PaymentStatus
)


class InvoiceModelTest(TestCase):
    def setUp(self):
        # Create User
        self.user = User.objects.create_user(
            username='@testuser',
            email='test@example.com',
            password='testpassword',
            first_name='Test',
            last_name='User'
        )

        # Create Student
        self.student = Student.objects.create(user=self.user)

        # Create Tutor
        self.tutor_user = User.objects.create_user(
            username='@testtutor',
            email='tutor@example.com',
            password='testpassword',
            first_name='Test',
            last_name='Tutor'
        )
        self.tutor = Tutor.objects.create(user=self.tutor_user)

        # Create Subject
        self.subject = Subject.objects.create(name='Test Subject')

        # Create Term
        self.term = Term.objects.create(
            start_date=date.today(),
            end_date=date.today() + timedelta(days=90)
        )

        # Create Lesson
        self.lesson = Lesson.objects.create(
            tutor=self.tutor,
            student=self.student,
            subject=self.subject,
            term=self.term,
            frequency='W',
            duration=timedelta(hours=1),
            start_date=date.today(),
            price_per_lesson=50
        )

        # Create LessonStatus
        self.lesson_status = LessonStatus.objects.create(
            lesson_id=self.lesson,
            date=date.today(),
            time='10:00:00',
            status='Completed',
            invoiced=False
        )

        # Create Invoice
        self.invoice = Invoice.objects.create(
            student=self.student,
            amount=100.00,
            status=PaymentStatus.UNPAID,
            due_date=date.today() + timedelta(days=30)
        )

        # Create the InvoiceLessonLink
        InvoiceLessonLink.objects.create(
            invoice=self.invoice,
            lesson=self.lesson_status
        )

    def test_valid_invoice_creation(self):
        try:
            self.invoice.full_clean()
        except ValidationError:
            self.fail("Test invoice should be valid")
        self.assertEqual(self.invoice.student, self.student)
        self.assertEqual(self.invoice.amount, 100.00)
        self.assertEqual(self.invoice.status, PaymentStatus.UNPAID)

    def test_mark_as_paid(self):
        self.invoice.mark_as_paid()
        self.invoice.refresh_from_db()
        self.lesson_status.refresh_from_db()
        self.assertEqual(self.invoice.status, PaymentStatus.PAID)
        self.assertTrue(self.lesson_status.invoiced)

    def test_check_if_overdue(self):
        self.invoice.due_date = date.today() - timedelta(days=1)
        self.invoice.check_if_overdue()
        self.assertEqual(self.invoice.status, PaymentStatus.OVERDUE)

    def test_get_total_hours(self):
        total_hours = self.invoice.get_total_hours()
        self.assertEqual(total_hours, 1.0)  # Based on the lesson duration we set

    def test_overdue_check_on_unpaid_invoice(self):
        """Ensure that an unpaid invoice past its due date is marked as overdue."""
        self.invoice.due_date = date.today() - timedelta(days=1)
        self.invoice.status = PaymentStatus.UNPAID
        self.invoice.save()

        self.invoice.check_if_overdue()
        self.invoice.refresh_from_db()

        self.assertEqual(self.invoice.status, PaymentStatus.OVERDUE)

    def test_validation_error_due_date_in_past(self):
        """Ensure validation raises an error if the due date is in the past."""
        self.invoice.due_date = date.today() - timedelta(days=1)

        with self.assertRaises(ValidationError) as cm:
            self.invoice.full_clean()  # Triggers the `clean` method

        self.assertIn("Due date cannot be in the past.", str(cm.exception))

    def test_due_date_present_validation(self):
        """Ensure validation raises an error if the due date is missing."""
        self.invoice.due_date = None

        with self.assertRaises(ValidationError) as cm:
            self.invoice.full_clean()

        self.assertIn("Due date cannot be empty.", str(cm.exception))

    def test_check_if_overdue_updates_to_overdue(self):
        """Ensure an unpaid invoice past its due date becomes overdue."""
        self.invoice.due_date = date.today() - timedelta(days=1)
        self.invoice.status = PaymentStatus.UNPAID
        self.invoice.save()

        self.invoice.check_if_overdue()
        self.invoice.refresh_from_db()

        self.assertEqual(self.invoice.status, PaymentStatus.OVERDUE)

    def test_check_if_overdue_does_not_update_if_already_overdue(self):
        """Ensure `check_if_overdue` does nothing if the status is already OVERDUE."""
        self.invoice.due_date = date.today() - timedelta(days=1)
        self.invoice.status = PaymentStatus.OVERDUE  # Already overdue
        self.invoice.save()

        # Call the method again
        self.invoice.check_if_overdue()
        self.invoice.refresh_from_db()

        self.assertEqual(self.invoice.status, PaymentStatus.OVERDUE)

    def test_check_if_overdue_no_change_if_not_past_due(self):
        """Ensure `check_if_overdue` does not update if due date is not in the past."""
        self.invoice.due_date = date.today() + timedelta(days=1)  # Future due date
        self.invoice.status = PaymentStatus.UNPAID
        self.invoice.save()

        # Call the method
        self.invoice.check_if_overdue()
        self.invoice.refresh_from_db()

        self.assertEqual(self.invoice.status, PaymentStatus.UNPAID)

    def test_check_if_overdue_skips_if_already_overdue(self):
        """Ensure that no changes occur when the invoice status is already OVERDUE."""
        # Set the invoice to an overdue state
        self.invoice.due_date = date.today() - timedelta(days=1)
        self.invoice.status = PaymentStatus.OVERDUE  # Already marked as overdue
        self.invoice.save()

        # Call the method
        self.invoice.check_if_overdue()

        # Ensure the status remains unchanged
        self.assertEqual(self.invoice.status, PaymentStatus.OVERDUE)

    def test_check_if_overdue_no_change_if_status_not_overdue(self):
        """Ensure `check_if_overdue` does not update if the status is not OVERDUE."""
        # Set the invoice status to something other than OVERDUE, e.g., PAID
        self.invoice.due_date = date.today() - timedelta(days=1)  # Past due
        self.invoice.status = PaymentStatus.PAID  # Already marked as PAID
        self.invoice.save()

        # Call the `check_if_overdue` method
        self.invoice.check_if_overdue()

        # Reload the invoice from the database to check for changes
        self.invoice.refresh_from_db()

        # Assert that the status has not changed to OVERDUE
        self.assertEqual(self.invoice.status, PaymentStatus.PAID)
