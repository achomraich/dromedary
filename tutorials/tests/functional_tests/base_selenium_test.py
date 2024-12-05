# base_selenium_test.py
from datetime import timedelta

from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from tutorials.models import *
from datetime import datetime, date

class BaseSeleniumTest(StaticLiveServerTestCase):

    def seed_user_model(self):
        user_fixtures = [
            {'username': '@johndoe', 'email': 'john.doe@example.org',
             'first_name': 'John', 'last_name': 'Doe', 'role': 'Admin'},

            {'username': '@janedoe', 'email': 'jane.doe@example.org',
             'first_name': 'Jane', 'last_name': 'Doe', 'role': 'Tutor'},

            {'username': '@charlie', 'email': 'charlie.johnson@example.org',
             'first_name': 'Charlie', 'last_name': 'Johnson', 'role': 'Student'},

            {'username': '@student', 'email': 'student.example1@example.org',
             'first_name': 'StudentName', 'last_name': 'StudentSurname', 'role': 'Student'}
        ]
        self.test_password = "Qa1"

        for data in user_fixtures:
            self.user = User.objects.create_user(
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
            {"start_date": "2024-09-01", "end_date": "2025-01-15"},
            {"start_date": "2025-02-01", "end_date": "2025-04-30"},
            {"start_date": "2025-05-01", "end_date": "2025-07-15"}
        ]
        for term_data in term_dates:
            Term.objects.create(
                start_date=term_data["start_date"],
                end_date=term_data["end_date"]
            )

    def seed_subject_model(self):
        subjects = [{"name": "C++"},
                    {"name": "Java"},
                    {"name": "Python"}]

        for s in subjects:
            Subject.objects.create(name=s["name"])

    def seed_lessons_model(self):
        lessons = [
            {
            'tutor': Tutor.objects.get(pk=2),
            'student': Student.objects.get(pk=3),
            'subject_id': Subject.objects.get(pk=1),
            'term_id': Term.objects.get(pk=1),
            'frequency': 'W',
            'duration': timedelta(hours=2, minutes=30),
            'start_date': "2024-09-01",
            'price_per_lesson': 20
            },

            {
            'tutor': Tutor.objects.get(pk=2),
            'student': Student.objects.get(pk=3),
            'subject_id': Subject.objects.get(pk=2),
            'term_id': Term.objects.get(pk=2),
            'frequency': 'M',
            'duration': timedelta(hours=2, minutes=30),
            'start_date': "2025-02-01",
            'price_per_lesson': 30
            },

            {
            'tutor': Tutor.objects.get(pk=2),
            'student': Student.objects.get(pk=3),
            'subject_id': Subject.objects.get(pk=3),
            'term_id': Term.objects.get(pk=3),
            'frequency': 'D',
            'duration': timedelta(hours=2, minutes=30),
            'start_date': "2025-03-01",
            'price_per_lesson': 10
            }]

        for lesson in lessons:
            Lesson.objects.create(
                tutor=lesson["tutor"],
                student=lesson["student"],
                subject_id=lesson["subject_id"],
                term_id=lesson["term_id"],
                frequency=lesson["frequency"],
                duration=lesson["duration"],
                start_date=lesson["start_date"],
                price_per_lesson=lesson["price_per_lesson"]
            )

    def seed_lessonStatus_model(self):

        lessonStatus = [
            {'lesson_id': Lesson.objects.get(pk=1),
             'date': "2024-10-05", 'time': "12:00:00", 'status': "Completed", 'feedback': ''},
            {'lesson_id': Lesson.objects.get(pk=1),
             'date': "2024-10-12", 'time': "12:00:00", 'status': "Completed", 'feedback': ''},
            {'lesson_id': Lesson.objects.get(pk=2),
             'date': "2024-10-05", 'time': "15:30:00", 'status': "Completed", 'feedback': ''},
            {'lesson_id': Lesson.objects.get(pk=2),
             'date': "2024-10-12", 'time': "14:00:00", 'status': "Cancelled", 'feedback': ''},
            {'lesson_id': Lesson.objects.get(pk=3),
             'date': "2024-12-06", 'time': "19:30:00", 'status': "Booked", 'feedback': ''},
            {'lesson_id': Lesson.objects.get(pk=3),
             'date': "2024-12-12", 'time': "09:00:00", 'status': "Booked", 'feedback': ''}
        ]

        for status_data in lessonStatus:
            LessonStatus.objects.create(
                lesson_id=status_data['lesson_id'],
                date=datetime.strptime(status_data['date'], '%Y-%m-%d').date(),
                time=status_data['time'],
                status=status_data['status'],
                feedback=status_data['feedback'],
                invoiced=False
            )

    def lessons_number(self):
        return len(Lesson.objects.all())

    @classmethod
    def setUpClass(cls):

        super().setUpClass()
        cls.seed_user_model(cls)
        cls.seed_term_model(cls)
        cls.seed_subject_model(cls)
        cls.seed_lessons_model(cls)
        cls.seed_lessonStatus_model(cls)
        #cls.driver = webdriver.Chrome()

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        super().tearDownClass()
