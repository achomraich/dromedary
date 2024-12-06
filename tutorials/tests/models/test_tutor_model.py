
'''
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from tutorials.models import Tutor, User


class TutorModelTest(TestCase):

    def setUp(self):

        self.user = User.objects.create_user(
            username="@tutor1",
            first_name="John",
            last_name="Doe",
            email="johndoe@example.com",
            password="Password123"
        )

        self.tutor = Tutor.objects.create(user=self.user)
'''
"""Unit tests for the Tutor model."""
from django.core.exceptions import ValidationError
from django.test import TestCase
from tutorials.models import User
from tutorials.models import Tutor

class TutorModelTestCase(TestCase):
    """Unit tests for the Tutor model."""

    fixtures = [
        'tutorials/tests/fixtures/default_user.json',
        'tutorials/tests/fixtures/other_users.json'
    ]

    GRAVATAR_URL = "https://www.gravatar.com/avatar/363c1b0cd64dadffb867236a00e62986"

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.tutor = Tutor.objects.create(user=self.user)

    def test_tutor_one_to_one_user(self):
        self.assertEqual(self.tutor.user, self.user)

    def test_valid_tutor_is_valid(self):
        try:
            self.tutor.full_clean()
        except ValidationError:
            self.fail('Default test tutor should be deemed valid.')
            
'''            self.fail("Default test tutor should be deemed valid!")

    def test_tutor_creation(self):
        self.assertEqual(self.tutor.user, self.user)
        self.assertEqual(self.tutor.user.first_name, "John")
        self.assertEqual(self.tutor.user.last_name, "Doe")

    def test_full_name_method(self):
        self.assertEqual(self.tutor.user.full_name(), "John Doe")

    def test_update_tutor(self):
        self.user.first_name = "Jane"
        self.user.save()
        self.assertEqual(self.tutor.user.first_name, "Jane")

    def test_delete_user_deletes_tutor(self):
        self.user.delete()
        with self.assertRaises(Tutor.DoesNotExist):
            Tutor.objects.get(user=self.user)

    def test_tutor_without_user(self):
        with self.assertRaises(IntegrityError):
            Tutor.objects.create(user=None)'''
