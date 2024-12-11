# DromeDary > tutorials folder > tests > models folder > test_invoice_model.py

from django.test import TestCase
from django.core.exceptions import ValidationError
from datetime import date, timedelta
from tutorials.models.models import (
    Invoice, Student, User, LessonStatus, Tutor,
    Subject, Term, Lesson, InvoiceLessonLink
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
            subject_id=self.subject,
            term_id=self.term,
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
            status='UNPAID',
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
        self.assertEqual(self.invoice.status, 'UNPAID')

    def test_mark_as_paid(self):
        self.invoice.mark_as_paid()
        self.invoice.refresh_from_db()
        self.lesson_status.refresh_from_db()
        self.assertEqual(self.invoice.status, 'PAID')
        self.assertTrue(self.lesson_status.invoiced)

    def test_check_if_overdue(self):
        self.invoice.due_date = date.today() - timedelta(days=1)
        self.invoice.check_if_overdue()
        self.assertEqual(self.invoice.status, 'OVERDUE')

    def test_get_total_hours(self):
        total_hours = self.invoice.get_total_hours()
        self.assertEqual(total_hours, 1.0)  # Based on the lesson duration we set

    def test_str_representation(self):
        expected_str = f"Invoice #{self.invoice.id} - {self.student.user.full_name()}"
        self.assertEqual(str(self.invoice), expected_str)