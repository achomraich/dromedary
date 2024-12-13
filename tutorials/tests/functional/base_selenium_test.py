from datetime import timedelta
from django.core.exceptions import ObjectDoesNotExist  # Add this import at the top

from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from tutorials.models import *
from datetime import datetime, date
from django.test import TransactionTestCase
from django.test import TestCase


class BaseSeleniumTest(TestCase):

    def seed_user_model(self):
        user_fixtures = [
            {'id': 1, 'username': '@johndoe', 'email': 'john.doe@example.org',
             'first_name': 'John', 'last_name': 'Doe', 'role': 'Admin'},

            {'id': 2, 'username': '@janedoe', 'email': 'jane.doe@example.org',
             'first_name': 'Jane', 'last_name': 'Doe', 'role': 'Tutor'},

            {'id': 3, 'username': '@charlie', 'email': 'charlie.johnson@example.org',
             'first_name': 'Charlie', 'last_name': 'Johnson', 'role': 'Student'},

            {'id': 4, 'username': '@tutor', 'email': 'tutor.example1@example.org',
             'first_name': 'TutorName', 'last_name': 'TutorSurname', 'role': 'Tutor'},

            {'id': 5, 'username': '@student', 'email': 'student.example1@example.org',
             'first_name': 'StudentName', 'last_name': 'StudentSurname', 'role': 'Student'}
        ]
        self.test_password = "Qa1"

        for data in user_fixtures:
            self.user = User.objects.create_user(
                id=data['id'],
                username=data['username'],
                email=data['email'],
                password=self.test_password,
                first_name=data['first_name'],
                last_name=data['last_name'],
            )
            if data['role'] == 'Admin':
                Admin.objects.create(user=self.user)
            elif data['role'] == 'Tutor':
                Tutor.objects.create(user=self.user)
            else:
                Student.objects.create(user=self.user)

    def seed_term_model(self):
        term_dates = [
            {"id": 1, "start_date": "2024-09-01", "end_date": "2025-01-15"},
            {"id": 2, "start_date": "2025-02-01", "end_date": "2025-04-30"},
            {"id": 3, "start_date": "2025-05-01", "end_date": "2025-07-15"}
        ]
        for term_data in term_dates:
            Term.objects.create(
                id=term_data["id"],
                start_date=term_data["start_date"],
                end_date=term_data["end_date"]
            )

    def seed_subject_model(self):
        subjects = [{'id': 1, "name": "C++", "description": "C++ course"},
                    {'id': 2, "name": "Java", "description": "Java course"},
                    {'id': 3, "name": "Python", "description": "Python course"}]

        for s in subjects:
            Subject.objects.create(id=s['id'], name=s["name"], description=s["description"])

    def seed_lessons_model(self):
        lessons = [
            {
                'id': 1,
                'tutor': Tutor.objects.get(pk=2),
                'student': Student.objects.get(pk=3),
                'subject': Subject.objects.get(pk=1),
                'term': Term.objects.get(pk=1),
                'frequency': 'W',
                'duration': timedelta(hours=2, minutes=30),
                'start_date': "2024-09-01",
                'price_per_lesson': 20
            },

            {
                'id': 2,
                'tutor': Tutor.objects.get(pk=2),
                'student': Student.objects.get(pk=3),
                'subject': Subject.objects.get(pk=2),
                'term': Term.objects.get(pk=2),
                'frequency': 'M',
                'duration': timedelta(hours=2, minutes=30),
                'start_date': "2025-02-01",
                'price_per_lesson': 30
            },

            {
                'id': 3,
                'tutor': Tutor.objects.get(pk=2),
                'student': Student.objects.get(pk=3),
                'subject': Subject.objects.get(pk=3),
                'term': Term.objects.get(pk=3),
                'frequency': 'D',
                'duration': timedelta(hours=2, minutes=30),
                'start_date': "2025-03-01",
                'price_per_lesson': 10
            }]

        for lesson in lessons:
            Lesson.objects.create(
                id=lesson["id"],
                tutor=lesson["tutor"],
                student=lesson["student"],
                subject=lesson["subject"],
                term=lesson["term"],
                frequency=lesson["frequency"],
                duration=lesson["duration"],
                start_date=lesson["start_date"],
                price_per_lesson=lesson["price_per_lesson"]
            )

    def seed_lessonStatus_model(self):

        lessonStatus = [
            {'id': Lesson.objects.get(pk=1),
             'date': "2024-10-05", 'time': "12:00:00", 'status': "Completed", 'feedback': ''},
            {'id': Lesson.objects.get(pk=1),
             'date': "2024-10-12", 'time': "12:00:00", 'status': "Completed", 'feedback': ''},
            {'id': Lesson.objects.get(pk=2),
             'date': "2024-10-05", 'time': "15:30:00", 'status': "Completed", 'feedback': ''},
            {'id': Lesson.objects.get(pk=2),
             'date': "2024-10-12", 'time': "14:00:00", 'status': "Cancelled", 'feedback': ''},
            {'id': Lesson.objects.get(pk=3),
             'date': "2024-12-06", 'time': "19:30:00", 'status': "Scheduled", 'feedback': ''},
            {'id': Lesson.objects.get(pk=3),
             'date': "2024-12-12", 'time': "09:00:00", 'status': "Scheduled", 'feedback': ''}
        ]

        for status_data in lessonStatus:
            LessonStatus.objects.create(
                lesson_id=status_data['id'],
                date=datetime.strptime(status_data['date'], '%Y-%m-%d').date(),
                time=status_data['time'],
                status=status_data['status'],
                feedback=status_data['feedback'],
                invoiced=False
            )

    def lessons_number_for_student(self, student=None):
        if not student:
            return Lesson.objects.all().count()
        user_object = User.objects.get(username=student)
        student_object = Student.objects.get(user=user_object)
        return Lesson.objects.filter(student=student_object).count()

    def subjects_number(self):
        return Subject.objects.all().count()

    def student_number(self):
        return Student.objects.all().count()

    def tutor_number(self):
        return Tutor.objects.all().count()

    def lessons_number_for_tutor(self, tutor=None):
        if not tutor:
            return Lesson.objects.all().count()
        user_object = User.objects.get(username=tutor)
        object = user_object
        try:
            object = Tutor.objects.get(user=user_object)
            print(f"Tutor: {object}")
        except ObjectDoesNotExist:
            object = None
            print(f"No Tutor object found for user: {user_object}")

        if object:
            return Lesson.objects.filter(tutor=object).count()

        try:
            object = Student.objects.get(user=user_object)
            print(f"Student: {object}")
        except ObjectDoesNotExist:
            object = None
            print(f"No Student object found for user: {user_object}")

        if object:
            return Lesson.objects.filter(student=object).count()


    def lessons_details_number(self, lesson_number):

        try:
            lesson_object = Lesson.objects.get(pk=lesson_number)
        except Lesson.DoesNotExist:
            raise ValueError(f"No Lesson found with lesson_id={lesson_number}")
        return LessonStatus.objects.filter(lesson_id=lesson_object).count()

    @classmethod
    def setUpTestData(cls):
        print("Seeding additional data in BaseListTests")

        cls.seed_user_model(cls)
        cls.seed_term_model(cls)
        cls.seed_subject_model(cls)
        cls.seed_lessons_model(cls)
        cls.seed_lessonStatus_model(cls)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def tearDown(self):
        from django.db import connection
        connection.queries.clear()
        super().tearDown()
