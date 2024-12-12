from django.test import TestCase
from tutorials.forms import InvoiceForm
from tutorials.models import Student, Subject, User
from datetime import date, timedelta


class InvoiceFormTest(TestCase):

    fixtures = [
        'tutorials/tests/fixtures/default_user.json',
        'tutorials/tests/fixtures/other_users.json',
        'tutorials/tests/fixtures/default_subject.json',
        'tutorials/tests/fixtures/default_tutor.json',
        'tutorials/tests/fixtures/default_term.json',
        'tutorials/tests/fixtures/default_student.json',
        'tutorials/tests/fixtures/default_lesson.json',
    ]

    def setUp(self):
        # Create test user
        self.user = User.objects.get(username='@johndoe')
        # Create student
        self.student = Student.objects.get(user__username='@janedoe')
        # Create subject.py
        self.subject = Subject.objects.get(name='Python')

        self.valid_form_data = {
            'student': self.student,
            'subject': self.subject,
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