from django.test import TestCase
from tutorials.forms import InvoiceForm
from tutorials.models.models import Student, Subject, User
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

        # Create student
        self.student = Student.objects.create(user=self.user)

        # Create subject.py
        self.subject = Subject.objects.create(name='Test Subject')

        self.valid_form_data = {
            'student': self.student.pk,
            'subject.py': self.subject.pk,
            'amount': 100.00,
            'due_date': (date.today() + timedelta(days=30)).strftime('%Y-%m-%d'),
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
        invalid_data['due_date'] = (date.today() - timedelta(days=1)).strftime('%Y-%m-%d')
        form = InvoiceForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('due_date', form.errors)