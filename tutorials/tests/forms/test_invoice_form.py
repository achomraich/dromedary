from django.test import TestCase
from tutorials.forms import InvoiceForm
from tutorials.models import Student, Subject, User
from datetime import date, timedelta


class InvoiceFormTest(TestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='@testuser',
            email='test@example.com',
            password='testpassword',
            first_name='Test',
            last_name='User'
        )

        self.student = Student.objects.create(user=self.user)

        self.subject = Subject.objects.create(name='Test Subject')

        self.valid_form_data = {
            'student': self.student.pk,
            'subject': self.subject.pk,
            'amount': 100.00,
            'due_date': '2025-01-15',
            'status': 'UNPAID'
        }

    def test_valid_form(self):
        form = InvoiceForm(data=self.valid_form_data)
        self.assertTrue(form.is_valid())

    def test_form_missing_data(self):
        invalid_data = self.valid_form_data.copy()
        invalid_data.pop('amount')
        form = InvoiceForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('amount', form.errors)

    def test_form_invalid_amount(self):
        invalid_data = self.valid_form_data.copy()
        invalid_data['amount'] = -100
        form = InvoiceForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('amount', form.errors)

    def test_form_past_due_date(self):
        invalid_data = self.valid_form_data.copy()
        invalid_data['due_date'] = '2024-09-01'
        form = InvoiceForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('due_date', form.errors)

    def test_student_label_from_instance(self):
        form = InvoiceForm()
        # Access the label generated for the student field's queryset
        student_label = form.fields['student'].label_from_instance(self.student)
        expected_label = f"{self.user.username} ({self.user.get_full_name()})"
        self.assertEqual(student_label, expected_label)

    def test_subject_label_from_instance(self):
        form = InvoiceForm()
        # Access the label generated for the subject field's queryset
        subject_label = form.fields['subject'].label_from_instance(self.subject)
        expected_label = f"{self.subject.name}"
        self.assertEqual(subject_label, expected_label)
