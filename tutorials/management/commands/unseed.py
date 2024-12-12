from django.core.management.base import BaseCommand, CommandError
from tutorials.models.shared import *
from tutorials.models.users import *
from tutorials.models.lessons import *
from tutorials.models.invoices import *
from tutorials.models.choices import *


from tutorials.models import (
    User, Admin, Student, Tutor, Lesson, Subject, Term,
    LessonStatus, Invoice, InvoiceLessonLink, LessonRequest,
    LessonUpdateRequest
)


class Command(BaseCommand):
    """Build automation command to unseed the database."""

    help = 'Unseeds the database by removing all sample data'

    def handle(self, *args, **options):
        """Unseed the database."""
        print("Starting database unseeding...")

        # Delete in order to respect foreign key constraints
        print("Deleting invoice links...")
        InvoiceLessonLink.objects.all().delete()

        print("Deleting invoices...")
        Invoice.objects.all().delete()

        print("Deleting lesson update requests...")
        LessonUpdateRequest.objects.all().delete()

        print("Deleting lesson requests...")
        LessonRequest.objects.all().delete()

        print("Deleting lesson statuses...")
        LessonStatus.objects.all().delete()

        print("Deleting lessons...")
        Lesson.objects.all().delete()

        print("Deleting subjects...")
        Subject.objects.all().delete()

        print("Deleting terms...")
        Term.objects.all().delete()

        # Delete users and their profiles
        print("Deleting user profiles...")
        Admin.objects.all().delete()
        Tutor.objects.all().delete()
        Student.objects.all().delete()

        print("Deleting users...")
        User.objects.filter(is_staff=False).delete()

        print("Database unseeding complete.")