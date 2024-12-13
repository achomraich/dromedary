from django.test import TestCase, Client
from django.urls import reverse
from tutorials.models import Lesson, LessonStatus, LessonUpdateRequest, Status, User, Student, Tutor, Term, Subject, Admin
from datetime import date, time, timedelta
from tutorials.forms import LessonFeedbackForm
from unittest.mock import patch

class ViewLessonsTests(TestCase):

    fixtures = [
        'tutorials/tests/fixtures/default_user.json',
        'tutorials/tests/fixtures/other_users.json',
        'tutorials/tests/fixtures/default_tutor.json',
        'tutorials/tests/fixtures/default_student.json',
        'tutorials/tests/fixtures/default_lesson.json',
        'tutorials/tests/fixtures/default_subject.json',
        'tutorials/tests/fixtures/default_term.json'
    ]

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
        self.lesson2 = Lesson.objects.create(
            tutor=self.tutor,
            student=self.student,
            subject=self.subject2,
            term=self.term,
            frequency="M",
            duration=timedelta(hours=1),
            start_date=date.today(),
            price_per_lesson=50,
            notes="Test lesson2"
        )

        self.lesson_status1 = LessonStatus.objects.create(
            lesson_id=self.lesson1,
            date=date(2023, 9, 15),
            time=time(10, 30),
            status=Status.SCHEDULED,
            feedback="Great session",
            invoiced=True,
        )

        self.lesson_status2 = LessonStatus.objects.create(
            lesson_id=self.lesson2,
            date=date(2025, 2, 15),
            time=time(12, 30),
            status=Status.SCHEDULED,
            feedback="Great session",
            invoiced=True,
        )

        self.student_user2 = User.objects.create_user(
            username='@student2',
            first_name='Student2Name',
            last_name='tudent2Surname',
            email='tsudent2@example.com',
            password='student2123'
        )
        self.student_user2.save()
        self.student2 = Student.objects.create(user=self.student_user2)

        self.tutor_user2 = User.objects.create_user(
            username='@tutor2',
            first_name='Tutor2Name',
            last_name='Tutor2Surname',
            email='tutor2@example.com',
            password='tutor2123'
        )
        self.tutor_user2.save()
        self.tutor2 = Tutor.objects.create(user=self.student_user2)

        self.lesson3 = Lesson.objects.create(
            tutor=self.tutor2,
            student=self.student2,
            subject=self.subject1,
            term=self.term,
            frequency="W",
            duration=timedelta(hours=1),
            start_date=date.today(),
            price_per_lesson=50,
            notes="Test lesson1"
        )

        self.lesson_status3 = LessonStatus.objects.create(
            lesson_id=self.lesson2,
            date=date(2025, 2, 15),
            time=time(19, 30),
            status=Status.SCHEDULED,
            feedback="Great session",
            invoiced=True,
        )

        # Set up lesson update requests
        self.lesson_update_request = LessonUpdateRequest.objects.create(lesson=self.lesson1, is_handled="N")

        self.client = Client()

    def test_admin_get_lesson_list(self):
        self.client.login(username='@admin', password='admin123')
        response = self.client.get(reverse('lessons_list'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.lesson1.subject.name)
        self.assertContains(response, self.lesson2.subject.name)
        self.assertContains(response, self.lesson3.subject.name)

    def test_student_get_lesson_list(self):
        self.client.login(username='@student', password='student123')
        response = self.client.get(reverse('lessons_list'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.lesson1.subject)
        self.assertContains(response, self.lesson2.subject)

    def test_tutor_get_lesson_list(self):
        self.client.login(username='@tutor', password='tutor123')
        response = self.client.get(reverse('lessons_list'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.lesson1.id)
        self.assertContains(response, self.lesson2.id)


    def test_lesson_detail_view(self):
        self.client.login(username='@student', password='student123')
        response = self.client.get(reverse('lesson_detail', args=[self.lesson1.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.lesson_status1.feedback)

    def test_cancel_lesson(self):
        self.client.login(username='@student', password='student123')
        response = self.client.post(reverse('cancel_lesson', args=[self.lesson_status2.pk]))

        self.assertRedirects(response, reverse('lesson_detail', args=[self.lesson2.pk]))

        self.lesson_status2.refresh_from_db()
        self.assertEqual(self.lesson_status2.status, Status.CANCELLED)

    def test_cancel_lesson_by_admin(self):
        self.client.login(username='@admin', password='admin123')
        response = self.client.post(reverse('cancel_lesson', args=[self.lesson_status2.pk]))

        self.assertRedirects(response, reverse('lesson_detail', args=[self.lesson2.pk]))

        self.lesson_status2.refresh_from_db()
        self.assertEqual(self.lesson_status2.status, Status.CANCELLED)

    def test_update_feedback_form_invalid_view(self):
        self.client.login(username='@student', password='student123')
        response = self.client.post(reverse('update_feedback', args=[self.lesson_status2.pk]),
                                    data={"feedback": "Great lesson!"})

        self.assertEqual(response.status_code, 200)

    def test_update_feedback_view(self):
        self.client.login(username='@tutor', password='tutor123')
        response = self.client.post(reverse('update_feedback', args=[self.lesson_status1.pk]),
                                    data={"feedback": "Great lesson!"})

        self.assertEqual(response.status_code, 302)  # Redirect after saving feedback
        self.lesson_status1.refresh_from_db()
        self.assertEqual(self.lesson_status1.feedback, "Great lesson!")

    def test_can_handle_request(self):
        self.client.login(username='@student', password='student123')
        response = self.client.get(reverse('lessons_list'))

        self.assertEqual(response.status_code, 200)
        self.assertIn(self.lesson1.pk, response.context['lessons_with_requests'])

    def test_filter_can_be_updated(self):
        self.client.login(username='@student', password='student123')
        response = self.client.get(reverse('lessons_list'))

        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(
            response.context['can_handle_request'].order_by('pk'),
            [self.lesson1.pk, self.lesson2.pk],
            transform=lambda x: x.pk
        )

    def test_post_no_lesson_id(self):
        self.client.login(username='@student', password='student123')
        response = self.client.post(reverse('lessons_list'))
        self.assertEqual(response.status_code, 302)

    def test_post_no_lesson_id(self):
        self.client.login(username='@student', password='student123')
        response = self.client.post(reverse('lessons_list'), data={'lesson_id': 3})
        self.assertEqual(response.status_code, 302)

    def test_post_update_feedback_by_tutor(self):
        self.client.login(username='@tutor', password='tutor123')
        response = self.client.post(reverse('update_feedback', args=[self.lesson_status1.pk]),
                                    data={'feedback': 'Updated feedback'})
        self.assertEqual(response.status_code, 302)  # Expect redirect
        self.lesson_status1.refresh_from_db()
        self.assertEqual(self.lesson_status1.feedback, 'Updated feedback')

    def test_post_cancel_lesson_by_student(self):
        self.client.login(username='@student', password='student123')
        response = self.client.post(reverse('cancel_lesson', args=[self.lesson_status3.pk]))
        self.assertRedirects(response, reverse('lesson_detail', args=[self.lesson2.pk]))
        self.lesson_status3.refresh_from_db()
        self.assertEqual(self.lesson_status3.status, Status.CANCELLED)

    def test_post_cancel_lesson_by_admin(self):
        self.client.login(username='@admin', password='admin123')
        response = self.client.post(reverse('cancel_lesson', args=[self.lesson_status3.pk]))
        self.assertRedirects(response, reverse('lesson_detail', args=[self.lesson2.pk]))
        self.lesson_status3.refresh_from_db()
        self.assertEqual(self.lesson_status3.status, Status.CANCELLED)

    def test_handle_lessons_form_save_exception(self):
        self.client.login(username='@tutor', password='tutor123')
        with patch('tutorials.forms.LessonFeedbackForm.save', side_effect=Exception("Save failed")):
            response = self.client.post(reverse('update_feedback', args=[self.lesson_status1.pk]),
                                        data={"feedback": "Some feedback"})
            self.assertEqual(response.status_code, 200)  # Renders the form again
            self.assertContains(response, "It was not possible to update this feedback")

    def test_lesson_detail_update_feedback(self):
        self.client.login(username='@tutor', password='tutor123')
        response = self.client.get(reverse('update_feedback', args=[self.lesson_status1.pk]))
        self.assertEqual(response.status_code, 200)

        self.assertContains(response, f"Edit Feedback: {self.lesson1.student.user.full_name()} ({self.lesson1.subject.name})")

    def test_lesson_detail_cancel_lesson(self):
        self.client.login(username='@student', password='student123')
        response = self.client.get(reverse('cancel_lesson', args=[self.lesson_status1.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.lesson_status1.status, Status.COMPLETED)

    def test_lesson_detail_access_by_admin(self):
        self.client.login(username='@admin', password='admin123')
        response = self.client.get(reverse('lesson_detail', args=[self.lesson1.pk]))
        self.assertEqual(response.status_code, 200)

        self.assertContains(response, "Great session")



