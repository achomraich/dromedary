from django.core.management.base import BaseCommand, CommandError

from tutorials.models.shared import *
from tutorials.models.users import *
from tutorials.models.lessons import *
from tutorials.models.invoices import *
from tutorials.models.choices import *


import pytz
from faker import Faker
from random import randint, random, choice
from datetime import timedelta, date, datetime, time

from tutorials.models import (
    User, Admin, Student, Tutor, Lesson, Subject, Term,
    LessonStatus, Invoice, InvoiceLessonLink, LessonRequest,
    LessonUpdateRequest
)

user_fixtures = [
    {'username': '@johndoe', 'email': 'john.doe@example.org', 'first_name': 'John', 'last_name': 'Doe',
     'role': 'Admin'},
    {'username': '@janedoe', 'email': 'jane.doe@example.org', 'first_name': 'Jane', 'last_name': 'Doe',
     'role': 'Tutor'},
    {'username': '@charlie', 'email': 'charlie.johnson@example.org', 'first_name': 'Charlie', 'last_name': 'Johnson',
     'role': 'Student'},
]

term_dates = [
    {'start_date': '2024-09-01', 'end_date': '2025-01-15'},
    {'start_date': '2025-02-01', 'end_date': '2025-04-30'},
    {'start_date': '2025-05-01', 'end_date': '2025-07-15'}
]

subjects = [
    {'name': 'Python', 'description': 'Simple Python to introduce beginners to programming.'},
    {'name': 'Java', 'description': 'Learn object-oriented programming with Java'},
    {'name': 'C++', 'description': ''},
    {'name': 'TypeScript', 'description': ''},
    {'name': 'Functional Programming', 'description': 'Scala/Haskell'},
    {'name': 'Web Development', 'description': 'Use HTML/CSS with Javascript to create interactive websites.'},
]

lessons = []
lesson_status = []


class Command(BaseCommand):
    """Build automation command to seed the database."""

    USER_COUNT = 150
    LESSON_COUNT = 200
    DEFAULT_PASSWORD = 'Password123'
    help = 'Seeds the database with sample data'

    def __init__(self):
        self.faker = Faker('en_GB')

    def handle(self, *args, **options):
        self.create_users()
        self.users = User.objects.all()
        self.create_other_models()
        self.seed_invoices()
        self.seed_lesson_requests()
        self.seed_update_requests()

    def create_other_models(self):
        self.create_terms()
        self.terms = Term.objects.all()

        self.create_subjects()
        self.subjects = Subject.objects.all()

        self.generate_random_lessons()
        self.lessons = Lesson.objects.all()

    def create_users(self):
        self.generate_user_fixtures()
        self.generate_random_users()

    def generate_user_fixtures(self):
        for data in user_fixtures:
            self.try_create_user(data)

    def generate_random_users(self):
        user_count = User.objects.count()
        while user_count < self.USER_COUNT:
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
        role = roles[randint(0, 2)]
        self.try_create_user(
            {'username': username, 'email': email, 'first_name': first_name, 'last_name': last_name, 'role': role})

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
        counter = 1
        for data in term_dates:
            try:
                Term.objects.create(
                    start_date=data["start_date"],
                    end_date=data["end_date"],
                    term_name=counter
                )
                counter += 1
                if counter > 3:
                    counter = 1
            except:
                pass

    def create_subjects(self):
        for data in subjects:
            try:
                existing_subject = Subject.objects.filter(name=data["name"]).first()
                if existing_subject:
                    print(f"Subject '{data['name']}' already exists.")
                else:
                    Subject.objects.create(name=data["name"], description=data["description"])
                    print(f"Subject '{data['name']}' added.")
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
        frequencies = [c[0] for c in Lesson.frequency.field.choices]

        tutor = choice(tutors)
        student = choice(students)
        subject = choice(all_subjects)
        term = choice(terms)
        frequency = choice(frequencies)
        duration = timedelta(hours=choice([1, 2]), minutes=choice([00, 15, 30, 45]))
        start_date = term.start_date
        price_per_lesson = choice([20, 30, 40, 50])

        if not Lesson.objects.filter(tutor=tutor, student=student, subject=subject).exists():
            self.create_lesson({
                'tutor': tutor,
                'student': student,
                'subject': subject,
                'term': term,
                'frequency': frequency,
                'duration': duration,
                'start_date': start_date,
                'price_per_lesson': price_per_lesson
            })

    def create_lesson(self, data):
        try:
            lesson = Lesson.objects.create(
                tutor=data["tutor"],
                student=data["student"],
                subject=data["subject"],
                term=data["term"],
                frequency=data["frequency"],
                duration=data["duration"],
                start_date=data["start_date"],
                price_per_lesson=data["price_per_lesson"]
            )
            tutor = data["tutor"]
            tutor.subjects.add(data["subject"])
            return lesson
        except:
            pass

    def seed_invoices(self):
        """Seed the database with sample invoices."""
        Invoice.objects.all().delete()
        InvoiceLessonLink.objects.all().delete()

        students = Student.objects.all()[:5]  # Get first 5 students
        statuses = ['UNPAID', 'PAID', 'OVERDUE']

        for i in range(5):  # Create 5 invoices
            try:
                student = choice(students)
                amount = randint(100, 500)
                status = choice(statuses)
                due_date = date.today() + timedelta(days=randint(-30, 30))

                invoice = Invoice.objects.create(
                    student=student,
                    amount=amount,
                    status=status,
                    due_date=due_date
                )

                lessons = LessonStatus.objects.filter(
                    lesson_id__student=student,
                    invoiced=False
                )[:2]

                for lesson in lessons:
                    InvoiceLessonLink.objects.create(
                        invoice=invoice,
                        lesson=lesson
                    )
                    lesson.invoiced = True
                    lesson.save()

                print(f"Seeding invoice {i+1}/5", end='\r')
            except Exception as e:
                print(f"Error creating invoice {i + 1}: {str(e)}")
                continue

        print("Invoice seeding complete.")

    def seed_lesson_requests(self):
        """Seed the database with sample lesson requests."""
        LessonRequest.objects.all().delete()

        students = Student.objects.all()[:5]
        subjects = Subject.objects.all()
        terms = Term.objects.all()

        frequencies = ['W', 'F', 'M', 'O']  # Weekly, Biweekly, Monthly, Once

        statuses = ['Pending', 'Booked', 'Cancelled', 'Completed', 'Confirmed', 'Rejected']

        for i in range(10):  # Create 10 lesson requests
            try:
                student = choice(students)
                subject = choice(subjects)
                term = choice(terms)
                frequency = choice(frequencies)
                status = choice(statuses)

                # Create a time between 9 AM and 5 PM
                hour = randint(9, 17)
                minute = choice([0, 15, 30, 45])
                lesson_time = time(hour, minute)

                request = LessonRequest.objects.create(
                    student=student,
                    subject=subject,
                    term=term,
                    time=lesson_time,
                    duration=timedelta(hours=1),
                    frequency=frequency,
                    status=status,
                    start_date=term.start_date + timedelta(days=randint(0, 30))
                )

                print(f"Seeding lesson request {i+1}/10", end='\r')
            except Exception as e:
                print(f"Error creating lesson request {i + 1}: {str(e)}")
                continue

        print("Lesson request seeding complete.")

    def seed_update_requests(self):
        """Seed the database with sample lesson update requests."""
        LessonUpdateRequest.objects.all().delete()

        lessons = Lesson.objects.filter(lessonstatus__status=Status.SCHEDULED).distinct()[:10]  # Get first 10 lessons
        update_options = ['1', '2', '3']  # Update options from model choices
        made_by_choices = ['Tutor', 'Student']
        handled_choices = ['N', 'Y']

        for index,lesson in enumerate(lessons):
            try:
                update_option = choice(update_options)
                made_by = choice(made_by_choices)
                is_handled = choice(handled_choices)

                # Generate appropriate details based on update option
                details = {
                    '1': 'Request to change tutor due to scheduling conflict',
                    '2': 'Need to change lesson time to accommodate other commitments',
                    '3': 'Cancelling future lessons due to course completion',
                }

                request = LessonUpdateRequest.objects.create(
                    lesson=lesson,
                    update_option=update_option,
                    details=details[update_option],
                    made_by=made_by,
                    is_handled=is_handled
                )

                if is_handled == 'N':
                    LessonStatus.objects.filter(lesson_id=lesson, status=Status.SCHEDULED).update(status=Status.PENDING)

                #print(f"Created update request for lesson {lesson.pk}")  # Changed from lesson_id to pk
                print(f"Seeding update request {index+1}/{len(lessons)}", end='\r')
            except Exception as e:
                print(f"Error creating update request: {str(e)}")
                continue

        print("Update request seeding complete.")

def create_username(first_name, last_name):
    return '@' + first_name.lower() + last_name.lower()


def create_email(first_name, last_name):
    return clean_and_lowercase(first_name) + '.' + clean_and_lowercase(last_name) + '@example.org'


def clean_and_lowercase(input_string):
    return ''.join(filter(str.isalpha, input_string)).lower()