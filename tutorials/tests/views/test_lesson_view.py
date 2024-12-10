from django.test import TestCase
from django.urls import reverse
from tutorials.models import Lesson, LessonStatus, LessonUpdateRequest, Status, User
from datetime import date, time

class ViewLessonsTests(TestCase):
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
        self.student = Admin.objects.create(user=self.student_user)
        self.tutor_user = Admin.objects.create(user=self.tutor_user)

        # Create a lesson and related statuses
        self.lesson = Lesson.objects.create(
            subject_id=1,  # Assuming subject_id is a foreign key
            student=self.student_user,
            tutor=self.tutor_user
        )
        self.lesson_status = LessonStatus.objects.create(
            lesson_id=self.lesson,
            status=Status.BOOKED,
            date=date.today(),
            time=time(10, 0),
            feedback=""
        )

        # Create a lesson update request
        self.lesson_update_request = LessonUpdateRequest.objects.create(
            lesson=self.lesson,
            is_handled="N"
        )
