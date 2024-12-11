from django.test import TestCase
from tutorials.models.models import Subject

from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError

class SubjectModelTest(TestCase):

    def setUp(self):
        self.subject = Subject.objects.create(
            name="Python",
            description="This is a test description for Python."
        )

    def test_valid_subject_is_valid(self):
        try:
            self.subject.full_clean()
        except ValidationError:
            self.fail("Default test subject should be deemed valid!")

    def test_subject_creation(self):
        subject = Subject.objects.get(name="Python")
        self.assertEqual(subject.name, "Python")
        self.assertEqual(subject.description, "This is a test description for Python.")

    def test_subject_str_representation(self):
        self.assertEqual(str(self.subject.name), "Python")

    def test_subject_name_max_length(self):
        subject = Subject.objects.get(name="Python")
        max_length = subject._meta.get_field('name').max_length
        self.assertEqual(max_length, 20)

    def test_subject_description_max_length(self):
        subject = Subject.objects.get(name="Python")
        max_length = subject._meta.get_field('description').max_length
        self.assertEqual(max_length, 255)

    def test_subject_without_name(self):
        with self.assertRaises(Exception):
            Subject.objects.create(description="No name provided.")

    def test_default_description(self):
        subject = Subject.objects.create(name="C++")
        self.assertEqual(subject.description, "")

    def test_invalid_description_length(self):
        long_description = "x" * 256
        subject = Subject(name="Python", description=long_description)
        with self.assertRaises(ValidationError):
            subject.full_clean()

    def test_invalid_name_length(self):
        long_name = "x" * 21
        subject = Subject(name=long_name, description="Test description")
        with self.assertRaises(ValidationError):
            subject.full_clean()

    def test_subject_without_name(self):
        with self.assertRaises(IntegrityError):
            Subject.objects.create(name=None, description="Test description")
