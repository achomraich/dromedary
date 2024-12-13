from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from tutorials.models import Lesson, LessonUpdateRequest, LessonStatus, Tutor, Student, Subject, Term, User, Admin, Status, TutorAvailability
from datetime import date, time, timedelta
from tutorials.views import TutorAvailabilityManager
from django.utils.timezone import now
from tutorials.models.choices import Days

class UpdateLessonViewTest(TestCase):
    fixtures = [
        'tutorials/tests/fixtures/default_user.json',
        'tutorials/tests/fixtures/other_users.json',
        'tutorials/tests/fixtures/default_subject.json',
        'tutorials/tests/fixtures/default_tutor.json',
        'tutorials/tests/fixtures/default_term.json',
        'tutorials/tests/fixtures/default_student.json',
    ]

    def setUp(self):
        # Set up a term

        self.tutor = Tutor.objects.get(user__username='@petrapickles')
        self.student = Student.objects.get(user__username='@rogersmith')
        self.subject1 = Subject.objects.get(name='Python')
        self.subject2 = Subject.objects.get(name='C++')
        self.term = Term.objects.get(start_date='2024-09-01')


        self.admin_user = User.objects.create_user(
            username='@admin',
            first_name='AdminName',
            last_name='AdminSurname',
            email='admin@example.com',
            password='admin123'
        )
        self.admin = Admin.objects.create(user=self.admin_user)


        self.term = Term.objects.create(
            start_date=date.today() - timedelta(days=30),
            end_date=date.today() + timedelta(days=30)
        )
        self.lesson = Lesson.objects.create(
            tutor=self.tutor,
            student=self.student,
            subject=self.subject1,
            term=self.term,
            frequency="W",
            duration=timedelta(hours=1),
            start_date='2025-01-15',
            price_per_lesson=50,
            notes="Test lesson1"
        )

        self.lesson_status = LessonStatus.objects.create(
            lesson_id=self.lesson,
            date=date(2025, 2, 10),
            time=time(12, 30),
            status=Status.PENDING,
            feedback="Great session",
            invoiced=True,
        )

        self.lesson_update_request = LessonUpdateRequest.objects.create(
            lesson=self.lesson,
            update_option='1',  # Assuming '1' means reschedule
            details="Change lesson time",
            made_by='Tutor',
            is_handled='N'
        )
        self.manager = TutorAvailabilityManager()


        TutorAvailability.objects.create(
            tutor=Tutor.objects.get(user__username='@petrapickles'),
            day=0,
            start_time="9:00",
            end_time="13:00",
            status="Available",
        )

        self.client = Client()

    def test_update_lesson_get(self):
        # Simulate a GET request to the view with lesson_id

        self.client.login(username='@admin', password='admin123')
        response = self.client.get(reverse('update_lesson', kwargs={'lesson_id': self.lesson.id}))

        # Check that the response status code is 200 and the correct template is used
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/manage_update_requests/update_lesson.html')

    def test_get_current_tutor_availability(self):
        availability = self.manager.get_current_tutor_availability(self.lesson.id)
        self.assertEqual(len(availability), 2)
        self.assertEqual(availability[1].day, "Sunday")  # Translates from integer to string

    def test_get_all_tutor_availability(self):
        all_availability = self.manager.get_all_tutor_availability()
        self.assertIn("Monday", all_availability)
        self.assertIn("09:00:00 - 13:00:00", all_availability["Monday"])
        self.assertEqual(len(all_availability["Monday"]["09:00:00 - 13:00:00"]), 1)

    def test_cancel_lesson_availability(self):
        self.manager.cancel_lesson_availability(self.lesson.id)
        lesson_status = LessonStatus.objects.filter(lesson_id=self.lesson.id).last()
        self.assertEqual(lesson_status.status, "Cancelled")
        updated_lesson = Lesson.objects.get(pk=self.lesson.pk)
        self.assertIn("All lessons were cancelled", updated_lesson.notes)


    def test_restore_old_tutor_availability(self):
        day = now().date()
        self.manager.restore_old_tutor_availability(
            tutor=self.tutor,
            day=date(2025, 2, 10),
            lesson_start_time="12:30:00",
            duration=timedelta(hours=1),
        )
        restored_availabilities = TutorAvailability.objects.filter(
            tutor=self.tutor, day=0, status="Available", start_time="12:30:00"
        )
        self.assertEqual(len(restored_availabilities), 0)  # Previous + restored slot

    def test_update_new_tutor_availability(self):
        day_mapping = {day[1]: day[0] for day in
                       Days.choices}  # Assuming Days.choices is like [(0, 'Monday'), (1, 'Tuesday'), ...]
        day_index = day_mapping.get("Monday")

        self.manager.restore_old_tutor_availability(
            tutor=self.tutor,
            day=date(2025, 2, 10),
            lesson_start_time="12:30:00",
            duration=timedelta(hours=1),
        )

        self.manager.update_new_tutor_availability(
            new_start_time="10:00",
            new_day=date(2025, 2, 10),
            duration=timedelta(hours=1),
            new_tutor=self.tutor,
        )

        updated_availability = TutorAvailability.objects.filter(
            tutor=self.tutor, status="Unavailable", day=0
        ).first()
        self.assertEqual(updated_availability.start_time.strftime("%H:%M:%S"), "10:00:00")
        self.assertEqual(updated_availability.end_time.strftime("%H:%M:%S"), "11:00:00")

    def test_merge_overlapping_availabilities(self):
        overlapping_slots = TutorAvailability.objects.filter(tutor=self.tutor)
        self.manager.merge_overlapping_availabilities(overlapping_slots)
        merged_availability = TutorAvailability.objects.filter(tutor=self.tutor)
        self.assertEqual(len(merged_availability), 1)  # Slots merged into one

    def test_update_lesson_statuses(self):
        old_date = now().date()
        next_date = now().date() + timedelta(weeks=1)
        end_date = now().date() + timedelta(weeks=4)

        self.manager.update_lesson_statuses(
            old_lesson_date=old_date,
            next_lesson_date=next_date,
            time="09:00:00",
            frequency="W",
            end_date=end_date,
            lesson_id=self.lesson.id,
        )

        statuses = LessonStatus.objects.filter(lesson_id=self.lesson.id)
        self.assertGreater(len(statuses), 0)