from django.test import TestCase,Client
from django.urls import reverse
from django.contrib.messages import get_messages
from tutorials.models import *
from tutorials.forms import UpdateLessonForm
from tutorials.views import UpdateLesson
from django.utils.timezone import now
from datetime import date, time, timedelta

class UpdateLessonTests(TestCase):


    def setUp(self):
        self.admin_user = User.objects.create_user(
            username='@johndoe',
            first_name='AdminName',
            last_name='AdminSurname',
            email='admin@example.com',
            password='Password123'
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
        self.tutor.subjects.add(self.subject1)
        self.tutor.subjects.add(self.subject2)
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
            status=Status.PENDING,
            feedback="Great session",
            invoiced=True,

        )
        self.slot1 = TutorAvailability.objects.create(
            tutor=Tutor.objects.get(user__username='@tutor'),
            day=5,
            start_time="17:00",
            end_time="19:00",
            status="Available",
        )
        self.slot1.save()

        self.slot2 = TutorAvailability.objects.create(
            tutor=Tutor.objects.get(user__username='@tutor'),
            day=6,
            start_time="12:30",
            end_time="13:30",
            status="Unavailable",
        )
        self.slot2.save()

        self.lesson_update_request = LessonUpdateRequest.objects.create(lesson=self.lesson1, is_handled="N", update_option='1', made_by='Tutor')
        self.form_input = {
            'instance': self.lesson1,
            'update_option':'1',
            'regular_lesson_time': '12:30:00',
            'day_of_week': 6,
            'next_lesson_date':'2024-12-20',
            'new_lesson_time': '17:00',
            'new_tutor': 3,
            'details': 'Change Tutor',

        }
        print(self.form_input['new_tutor'])
        self.client = Client()



    def test_get_method_calls_update_lesson(self):
        self.client.login(username='@johndoe', password='Password123')

        url = reverse("update_lesson", args=[self.lesson1.id])
        response = self.client.get(url)

        self.assertTemplateUsed(response, "admin/manage_update_requests/update_lesson.html")

    def test_post_method_with_lesson_id_redirects_correctly(self):
        self.client.login(username='@johndoe', password='Password123')
        url = reverse("update_lesson", args=[self.lesson1.id])
        response = self.client.post(url)

        # Assert redirection to update_requests
        self.assertRedirects(response, reverse("update_requests"))

    def test_update_lesson_with_cancel_option_calls_cancel_lesson(self):
        self.client.login(username='@johndoe', password='Password123')
        # Change update option to '3' for cancellation
        self.lesson_update_request.update_option = "3"
        self.lesson_update_request.save()

        url = reverse("update_lesson", args=[self.lesson1.id])
        response = self.client.get(url)

        # Assert redirection to lessons_list and appropriate message
        self.assertRedirects(response, reverse("lessons_list"))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "Lesson cancelled successfully.")

    def test_update_lesson_renders_form_for_update_options_1_or_2(self):
        self.client.login(username='@johndoe', password='Password123')
        # Update the request to use option '1'
        self.lesson_update_request.update_option = "1"
        self.lesson_update_request.save()

        url = reverse("update_lesson", args=[self.lesson1.id])
        response = self.client.get(url)

        self.assertTemplateUsed(response, "admin/manage_update_requests/update_lesson.html")
        self.assertIn("form", response.context)

    def test_cancel_lesson_no_pending_lessons(self):
        self.client.login(username='@johndoe', password='Password123')
        # Remove any pending lessons
        LessonStatus.objects.all().delete()

        url = reverse("update_lesson", args=[self.lesson1.id])
        response = self.client.get(url)

        # Assert appropriate message and handled status update
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "No lessons to reschedule!")
        self.lesson_update_request.refresh_from_db()
        self.assertEqual(self.lesson_update_request.is_handled, "Y")

    def test_prepare_update_form_with_no_pending_lessons(self):
        self.client.login(username='@johndoe', password='Password123')
        # Remove any pending lessons
        LessonStatus.objects.all().delete()

        url = reverse("update_lesson", args=[self.lesson1.id])
        response = self.client.get(url)

        # Assert appropriate message and absence of form in context
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "No lessons to reschedule!")
        #self.assertIsNone(response.context.get("form"))

    def test_prepare_update_form_with_valid_data(self):
        self.client.login(username='@johndoe', password='Password123')
        url = reverse("update_lesson", args=[self.lesson1.id])
        response = self.client.get(url)


        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], UpdateLessonForm)

    def test_save_form_updates_successfully(self):
        self.client.login(username='@johndoe', password='Password123')
        # Provide valid POST data for form submission
        url = reverse("update_lesson", args=[self.lesson1.id])
        response = self.client.post(url, data=self.form_input)


        self.assertRedirects(response, reverse("update_requests"))
        self.lesson_update_request.refresh_from_db()
        self.assertEqual(self.lesson_update_request.is_handled, "N")

    def test_post_invalid_form_returns_form_with_errors(self):
        self.client.login(username='@johndoe', password='Password123')
        # Provide invalid POST data to simulate form errors
        url = reverse("update_lesson", args=[self.lesson1.id])
        response = self.client.post(
            url,
            data={
                "new_tutor": "",  # Invalid data
                "new_day_of_week": "",
                "new_lesson_time": "",
            },
        )
        form = response.context.get('form')
        # Assert the form is returned with errors
        self.assertTrue(form.errors)

    def test_cancel_lesson_successfully(self):
        self.client.login(username='@johndoe', password='Password123')

        self.lesson_update_request.update_option='3'
        self.lesson_update_request.save()
        url = reverse("update_lesson", args=[self.lesson1.id])
        response = self.client.get(url)

        # Assert appropriate redirection and success message
        self.assertRedirects(response, reverse("lessons_list"))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "Lesson cancelled successfully.")
