from django.core.management.base import BaseCommand, CommandError

from tutorials.models import User, Admin, Student, Tutor, Lesson, LessonStatus, Subject, Term

import pytz
from faker import Faker
from random import randint, random, choice
from datetime import timedelta

user_fixtures = [
    {'username': '@johndoe', 'email': 'john.doe@example.org', 'first_name': 'John', 'last_name': 'Doe', 'role': 'Admin'},
    {'username': '@janedoe', 'email': 'jane.doe@example.org', 'first_name': 'Jane', 'last_name': 'Doe', 'role': 'Tutor'},
    {'username': '@charlie', 'email': 'charlie.johnson@example.org', 'first_name': 'Charlie', 'last_name': 'Johnson', 'role':'Student'},
]

term_dates = [
    {'start_date': '2024-09-01', 'end_date': '2025-01-15'},
    {'start_date': '2025-02-01', 'end_date': '2025-04-30'},
    {'start_date': '2025-05-01', 'end_date': '2025-07-15'}
]

subjects = [
    {'name': 'C++'},
    {'name': 'Java'},
    {'name': 'Python'}
]

lessons = []

lesson_status = []

class Command(BaseCommand):
    """Build automation command to seed the database."""

    USER_COUNT = 300
    DEFAULT_PASSWORD = 'Password123'
    help = 'Seeds the database with sample data'

    def __init__(self):
        self.faker = Faker('en_GB')

    def handle(self, *args, **options):
        self.create_users()
        self.users = User.objects.all()
        self.create_other_models()

    def create_other_models(self):
        create_other_defaults()

        self.create_terms()
        self.terms = Term.objects.all()

        self.create_subjects()
        self.subjects = Subject.objects.all()

        self.create_lessons()
        self.lessons = Lesson.objects.all()

        self.create_lesson_status()
        self.lesson_status = LessonStatus.objects.all()

    def create_users(self):
        self.generate_user_fixtures()
        self.generate_random_users()

    def generate_user_fixtures(self):
        for data in user_fixtures:
            self.try_create_user(data)

    def generate_random_users(self):
        user_count = User.objects.count()
        while  user_count < self.USER_COUNT:
            print(f"Seeding user {user_count}/{self.USER_COUNT}", end='\r')
            self.generate_user()
            user_count = User.objects.count()
        print("User seeding complete.      ")

    def generate_user(self):
        first_name = self.faker.first_name()
        last_name = self.faker.last_name()
        email = create_email(first_name, last_name)
        username = create_username(first_name, last_name)
        roles = ['Admin', 'Tutor', 'Student']
        role = roles[randint(0,2)]
        self.try_create_user({'username': username, 'email': email, 'first_name': first_name, 'last_name': last_name, 'role': role})
       
    def try_create_user(self, data):
        try:
            self.create_user(data)
        except:
            pass

    def create_user(self, data):
        user = User.objects.create_user(
            username=data['username'],
            email=data['email'],
            password=Command.DEFAULT_PASSWORD,
            first_name=data['first_name'],
            last_name=data['last_name'],
        )

        if data['role'] == 'Admin':
            Admin.objects.create(user=user)
        elif data['role'] == 'Tutor':
            Tutor.objects.create(user=user)
        else:
            Student.objects.create(user=user)

    def create_terms(self):
        for data in term_dates:
            try:
                Term.objects.create(
                    start_date=data["start_date"],
                    end_date=data["end_date"]
                )
            except:
                pass

    def create_subjects(self):
        for data in subjects:
            try:
                Subject.objects.create(name=data["name"])
            except:
                pass

    def create_lessons(self):
        for data in lessons:
            try:
                Lesson.objects.create(
                    tutor=data["tutor"],
                    student=data["student"],
                    subject_id=data["subject_id"],
                    term_id=data["term_id"],
                    frequency=data["frequency"],
                    duration=data["duration"],
                    start_date=data["start_date"],
                    price_per_lesson=data["price_per_lesson"]
                )
                print("lesson added.")
            except:
                pass

    def create_lesson_status(self):
        for data in lesson_status:
            try:
                LessonStatus.objects.create(
                    lesson_id=data['lesson_id'],
                    date=data['date'],
                    time=data['time'],
                    status=data['status'],
                    feedback=data['feedback'],
                    invoiced=False
                )
                print("one lesson_status added.")
            except:
                pass

def create_username(first_name, last_name):
    return '@' + first_name.lower() + last_name.lower()

def create_email(first_name, last_name):
    return first_name + '.' + last_name + '@example.org'

def create_other_defaults():
    global lessons, lesson_status
    tutors = Tutor.objects.all()
    students = Student.objects.all()
    lessons = [
        {
            'tutor': choice(tutors),
            'student': choice(students),
            'subject_id': Subject.objects.get(subject_id='2'),
            'term_id': Term.objects.get(term_id='1'),
            'frequency': 'W',
            'duration': timedelta(hours=2, minutes=30),
            'start_date': "2024-09-01",
            'price_per_lesson': 20
        },
        {
            'tutor': choice(tutors),
            'student': choice(students),
            'subject_id': Subject.objects.get(subject_id='2'),
            'term_id': Term.objects.get(term_id='2'),
            'frequency': 'M',
            'duration': timedelta(hours=2, minutes=30),
            'start_date': "2025-02-01",
            'price_per_lesson': 30
        }
    ]
    print("lessons added.")
    all_lessons = Lesson.objects.all()
    lesson_status = [
        {'lesson_id': choice(all_lessons),
         'date': "2024-10-05", 'time': "12:00:00", 'status': "Completed", 'feedback': ''},
        {'lesson_id': choice(all_lessons),
         'date': "2024-10-05", 'time': "12:00:00", 'status': "Completed", 'feedback': ''},
        {'lesson_id': choice(all_lessons),
         'date': "2024-10-05", 'time': "15:30:00", 'status': "Completed", 'feedback': ''},
        {'lesson_id': choice(all_lessons),
         'date': "2024-10-05", 'time': "14:00:00", 'status': "Pending", 'feedback': ''},
        {'lesson_id': choice(all_lessons),
         'date': "2024-10-05", 'time': "19:30:00", 'status': "Pending", 'feedback': ''},
        {'lesson_id': choice(all_lessons),
         'date': "2024-10-05", 'time': "09:00:00", 'status': "Pending", 'feedback': ''}
    ]
    print("lesson_status added.")