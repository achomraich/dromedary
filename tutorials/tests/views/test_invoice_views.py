from django.test import TestCase, Client
from django.urls import reverse
from tutorials.models import (
    Invoice, Student, User, Admin, Subject,
    Tutor, Term, Lesson, LessonStatus
)
from datetime import date, timedelta
from django.contrib.messages import get_messages


class InvoiceViewsTest(TestCase):

    fixtures = [
        'tutorials/tests/fixtures/default_user.json',
        'tutorials/tests/fixtures/other_users.json',
        'tutorials/tests/fixtures/default_tutor.json',
        'tutorials/tests/fixtures/default_student.json',
        'tutorials/tests/fixtures/default_lesson.json',
        'tutorials/tests/fixtures/default_subject.json',
        'tutorials/tests/fixtures/default_term.json',
    ]

    def setUp(self):
        # Create admin user
        self.admin_user = User.objects.get(username='@johndoe')
        self.admin = Admin.objects.create(user=self.admin_user)

        # Create student user
        self.student = Student.objects.get(user__username='@janedoe')

        # Create subject.py
        self.subject = Subject.objects.get(name='Python')

        # Create invoice
        self.invoice = Invoice.objects.create(
            student=self.student,
            amount=100.00,
            status='UNPAID',
            due_date=date.today() + timedelta(days=30)
        )

        # Setup client and login
        self.client.login(username='@johndoe', password='Password123')

        # Setup URLs
        self.list_url = reverse('invoice_list')
        self.create_url = reverse('create_invoice')
        self.detail_url = reverse('invoice_detail', args=[self.invoice.id])

    def test_invoice_list_view(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'invoices/invoice_list.html')
        self.assertContains(response, self.invoice.student.user.full_name())

    def test_create_invoice_view(self):
        response = self.client.get(self.create_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'invoices/create_invoice.html')

    def test_invoice_detail_view(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'invoices/invoice_detail.html')
        self.assertContains(response, self.invoice.student.user.full_name())

    def test_create_invoice_post(self):
        # Create a lesson status that can be invoiced
        lesson_status = LessonStatus.objects.create(
            lesson_id=Lesson.objects.create(
                tutor=Tutor.objects.create(user=User.objects.create_user(
                    username='@testtutor',
                    email='tutor@test.com',
                    password='Password123'
                )),
                student=self.student,
                subject=self.subject,
                term=Term.objects.create(
                    start_date=date.today(),
                    end_date=date.today() + timedelta(days=90)
                ),
                frequency='W',
                duration=timedelta(hours=1),
                start_date=date.today(),
                price_per_lesson=50
            ),
            date=date.today(),
            time='10:00:00',
            status='Completed',
            invoiced=False
        )

        new_invoice_data = {
            'student': self.student.pk,
            'subject': self.subject.pk,
            'amount': 150.00,
            'due_date': (date.today() + timedelta(days=30)).strftime('%Y-%m-%d'),
            'status': 'UNPAID'
        }
        response = self.client.post(self.create_url, new_invoice_data, follow=False)
        self.assertRedirects(response, reverse('invoice_list'))
        self.assertTrue(Invoice.objects.filter(amount=150.00).exists())

    def test_mark_invoice_as_paid(self):
        response = self.client.post(self.detail_url, {'mark_paid': 'true'})
        self.assertEqual(response.status_code, 302)
        updated_invoice = Invoice.objects.get(id=self.invoice.id)
        self.assertEqual(updated_invoice.status, 'PAID')

    def test_delete_invoice(self):
        response = self.client.post(self.detail_url, {'delete': 'true'})
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Invoice.objects.filter(id=self.invoice.id).exists())

    def test_post_null_invoice(self):
        response = self.client.post(self.detail_url, {})
        self.assertRedirects(response, self.detail_url)

    def test_unauthorized_access(self):
        self.client.logout()
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 302)

    def test_create_invoice_invalid_form(self):
        # Simulate submitting a form with invalid data
        invalid_invoice_data = {
            'student': '',  # Missing student field
            'amount': '',  # Missing amount field
            'due_date': '',  # Missing due date field
            'status': '',  # Missing status field
        }

        response = self.client.post(self.create_url, invalid_invoice_data)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'invoices/create_invoice.html')
        self.assertContains(response, "This field is required.")  # Check for validation errors

        self.assertEqual(Invoice.objects.count(), 1)

    def test_create_invoice_no_uninvoiced_lessons(self):
        new_invoice_data = {
            'student': self.student.pk,
            'subject': self.subject.pk,
            'amount': 150.00,
            'due_date': (date.today() + timedelta(days=30)).strftime('%Y-%m-%d'),
            'status': 'UNPAID'
        }
        response = self.client.post(self.create_url, new_invoice_data)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(str(messages_list[0]), "No uninvoiced lessons found for this student.")

        self.assertTemplateUsed(response, 'invoices/create_invoice.html')
        self.assertEqual(Invoice.objects.count(), 1)
