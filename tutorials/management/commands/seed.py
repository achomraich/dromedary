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
    {'name': 'Python'},
    {'name': 'JS'},
    {'name': 'Python'},
    {'name': 'TypeScript'},
    {'name': 'Scala'},
    {'name': 'Ruby'}
]

lessons = []

lesson_status = []

class Command(BaseCommand):
    """Build automation command to seed the database."""

    USER_COUNT = 300
    LESSON_COUNT = 100
    DEFAULT_PASSWORD = 'Password123'
    help = 'Seeds the database with sample data'

    def __init__(self):
        self.faker = Faker('en_GB')

    def handle(self, *args, **options):
        self.create_users()
        self.users = User.objects.all()
        self.create_other_models()

    def create_other_models(self):
        self.create_terms()
        self.terms = Term.objects.all()

        self.create_subjects()
        self.subjects = Subject.objects.all()

        self.lessons = Lesson.objects.all()

        self.generate_random_lessons()
        self.lessons = Lesson.objects.all()

        self.generate_random_lesson_status()
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
              
    def generate_random_lessons(self):
        lesson_count = Lesson.objects.count()
        while lesson_count < self.LESSON_COUNT:
            print(f"Seeding lesson {lesson_count}/{self.LESSON_COUNT}", end='\r')
            self.generate_lesson()
            lesson_count = Lesson.objects.count()
        print("Lesson seeding complete.      ")

    def generate_lesson(self):
        tutors = Tutor.objects.all()
        students = Student.objects.all()
        all_subjects = Subject.objects.all()
        terms = Term.objects.all()
        selectedTerm = choice(terms)

        tutor = choice(tutors)
        student = choice(students)
        subject_id = choice(all_subjects)
        term_id = selectedTerm
        frequency = choice(['W', 'M'])
        duration = timedelta(hours=choice([1,2]), minutes=choice([00,15,30,45]))
        start_date = selectedTerm.start_date
        price_per_lesson = choice([20, 30, 40, 50])
        self.create_lesson({'tutor': tutor, 'student': student, 'subject_id': subject_id, 'term_id': term_id, 'frequency': frequency, 'duration': duration, 'start_date': start_date, 'price_per_lesson': price_per_lesson})

    def create_lesson(self, data):
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
        except:
            pass

    def generate_random_lesson_status(self):
        lesson_count = Lesson.objects.count()
        all_lessons = Lesson.objects.all()
        lessons_with_status_count = 0
        while lessons_with_status_count < lesson_count:
            print(f"Seeding lesson status {lessons_with_status_count}/{lesson_count}", end='\r')
            self.generate_lesson_status({'lesson_id': all_lessons[lessons_with_status_count]})
            lessons_with_status_count += 1
        print("Lesson status seeding complete.      ")

    def generate_lesson_status(self, data):
        lesson_id = data["lesson_id"]

        term = lesson_id.term_id
        # Time and date not implemented randomization
        date = term.start_date
        time = "15:30:00"

        status = choice(['Scheduled', 'Completed', 'Cancelled'])
        feedback = choice(['Good progress', 'Needs improvement', 'Excellent'])
        self.create_lesson_status({'lesson_id': lesson_id, 'date': date, 'time': time, 'status': status, 'feedback': feedback})

    def create_lesson_status(self, data):
        try:
            LessonStatus.objects.create(
                lesson_id=data['lesson_id'],
                date=data['date'],
                time=data['time'],
                status=data['status'],
                feedback=data['feedback'],
                invoiced=False
            )
        except:
            pass

def create_username(first_name, last_name):
    return '@' + first_name.lower() + last_name.lower()

def create_email(first_name, last_name):
    return clean_and_lowercase(first_name) + '.' + clean_and_lowercase(last_name) + '@example.org'

def clean_and_lowercase(input_string):
    return ''.join(filter(str.isalpha, input_string)).lower()

