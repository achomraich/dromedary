from django.test import TestCase, Client
from django.urls import reverse
from tutorials.models import Lesson, LessonUpdateRequest, LessonStatus, Tutor, Student, Subject, Term, User, Admin, Status
from datetime import date, time, timedelta
from unittest.mock import patch

class UpdateLessonRequestTests(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username='@admin',
            first_name='AdminName',
            last_name='AdminSurname',
            email='admin@example.com',
            password='admin123'
        )

        self.student_user = User.objects.create_user(
            username='@student',
            first_name='StudentName',
            last_name='StudentSurname',
            email='student@example.com',
            password='student123'
        )

        self.tutor_user = User.objects.create_user(
            username='@tutor',
            first_name='TutorName',
            last_name='TutorSurname',
            email='tutor@example.com',
            password='tutor123'
        )
        self.admin_user.save()
        self.student_user.save()
        self.tutor_user.save()

        self.admin = Admin.objects.create(user=self.admin_user)
        self.student = Student.objects.create(user=self.student_user)
        self.tutor = Tutor.objects.create(user=self.tutor_user)

        self.subject1 = Subject.objects.create(name="Python")
        self.subject2 = Subject.objects.create(name="C++")
        self.subject1.save()
        self.subject2.save()

        self.term = Term.objects.create(
            start_date=date.today() - timedelta(days=30),
            end_date=date.today() + timedelta(days=30)
        )
        self.lesson1 = Lesson.objects.create(
            tutor=self.tutor,
            student=self.student,
            subject=self.subject1,
            term=self.term,
            frequency="W",
            duration=timedelta(hours=1),
            start_date=date.today(),
            price_per_lesson=50,
            notes="Test lesson1"
        )

        self.lesson_status1 = LessonStatus.objects.create(
            lesson_id=self.lesson1,
            date=date(2025, 2, 15),
            time=time(12, 30),
            status=Status.SCHEDULED,
            feedback="Great session",
            invoiced=True,
        )
        self.client = Client()

    def test_get_as_admin(self):
        self.client.login(username='@admin', password='admin123')

        response = self.client.get(reverse('update_requests'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/manage_update_requests/update_lesson_request_list.html')
        self.assertIn('list_of_requests', response.context)

    def test_get_as_non_admin(self):
        self.client.login(username='@student', password='student123')

        response = self.client.get(reverse('request_changes', args=[self.lesson1.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student/manage_lessons/request_changes.html')
        self.assertIn('form', response.context)
        self.assertIn('subject', response.context)

    def test_post_request_changes_as_student(self):
        self.client.login(username='@student', password='student123')

        response = self.client.post(
            reverse('request_changes', args=[self.lesson1.pk]),
            data={
                'update_option': '1',
                'details': 'Request to change tutor'
            }
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(LessonUpdateRequest.objects.filter(lesson=self.lesson1).exists())
        request_instance = LessonUpdateRequest.objects.get(lesson=self.lesson1, is_handled='N')
        self.assertEqual(request_instance.update_option, '1')
        self.assertEqual(request_instance.details, 'Request to change tutor')
        self.assertEqual(request_instance.made_by, 'Student')

    def test_post_request_changes_as_tutor(self):
        self.client.login(username='@tutor', password='tutor123')

        response = self.client.post(
            reverse('request_changes', args=[self.lesson1.pk]),
            data={
                'update_option': '2',
                'details': 'Request to change lesson time'
            }
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(LessonUpdateRequest.objects.filter(lesson=self.lesson1).exists())
        request_instance = LessonUpdateRequest.objects.get(lesson=self.lesson1)
        self.assertEqual(request_instance.update_option, '2')
        self.assertEqual(request_instance.details, 'Request to change lesson time')
        self.assertEqual(request_instance.made_by, 'Tutor')

    def test_invalid_form(self):

        self.client.login(username='@student', password='student123')

        response = self.client.post(
            reverse('request_changes', args=[self.lesson1.pk]),
            data={
                'update_option': '',
                'details': ''
            }
        )
        self.assertEqual(response.status_code, 200)  # Stays on the same page
        self.assertFalse(LessonUpdateRequest.objects.filter(lesson=self.lesson1).exists())
        self.assertFormError(response, 'form', 'update_option', 'This field is required.')

    def test_status_change(self):
        self.client.login(username='@student', password='student123')


        self.client.post(
            reverse('request_changes', args=[self.lesson1.pk]),
            data={
                'update_option': '3',
                'details': 'Cancel the lesson'
            }
        )

        self.lesson_status1.refresh_from_db()
        self.assertEqual(self.lesson_status1.status, 'Pending')

    def test_get_request_as_anonymous(self):
        response = self.client.get(reverse('request_changes', args=[self.lesson1.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('log_in'), response.url)

    def test_post_request_as_anonymous(self):
        response = self.client.post(
            reverse('request_changes', args=[self.lesson1.pk]),
            data={
                'update_option': '1',
                'details': 'Request to change tutor'
            },
            follow=False
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('log_in'), response.url)


    def test_post_redirects_to_lessons_list(self):
        self.client.login(username='@admin', password='admin123')

        # Trigger a POST request where the URL is valid but doesn't match `request_changes/`
        response = self.client.post(reverse('update_requests'), data={})

        # Verify redirect to lessons list
        self.assertRedirects(response, reverse('lessons_list'))


    def test_post_form_save_raises_exception(self):
        self.client.login(username='@student', password='student123')

        # Simulate an error when saving the form
        with patch('tutorials.forms.UpdateLessonRequestForm.save', side_effect=Exception("Test error")):
            response = self.client.post(
                reverse('request_changes', args=[self.lesson1.pk]),
                data={'update_option': '1', 'details': 'Error simulation'}
            )
            # Verify the form error is added
            self.assertEqual(response.status_code, 200)
            self.assertFormError(response, 'form', None, "An error occurred: Test error")

    def test_post_request_changes_as_student_branch(self):
        self.client.login(username='@student', password='student123')

        # Submit a valid request to trigger the student branch
        response = self.client.post(
            reverse('request_changes', args=[self.lesson1.pk]),
            data={'update_option': '1', 'details': 'Request to change tutor'}
        )

        # Verify the request is created and the branch for students is used
        self.assertEqual(response.status_code, 302)
        request_instance = LessonUpdateRequest.objects.get(lesson=self.lesson1, is_handled='N')
        self.assertEqual(request_instance.made_by, 'Student')

    def test_change_status_with_valid_instance(self):
        self.client.login(username='@student', password='student123')

        # Submit a valid request to create a LessonUpdateRequest instance
        response = self.client.post(
            reverse('request_changes', args=[self.lesson1.pk]),
            data={'update_option': '3', 'details': 'Cancel the lesson'}
        )

        # Ensure the status is updated
        self.lesson_status1.refresh_from_db()
        self.assertEqual(self.lesson_status1.status, 'Pending')

    def test_update_request_without_account_instance(self):
        response = self.client.get(reverse('update_requests'))
        expected_redirect_url = f"{reverse('log_in')}?next={reverse('update_requests')}"
        self.assertRedirects(response, expected_redirect_url)

