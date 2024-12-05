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

    def test_valid_tutor_is_valid(self):
        try:
            self.tutor.full_clean()
        except ValidationError:
            self.fail("Default test tutor should be deemed valid!")

    def test_tutor_creation(self):
        self.assertEqual(self.tutor.user, self.user)
        self.assertEqual(self.tutor.user.first_name, "John")
        self.assertEqual(self.tutor.user.last_name, "Doe")

    def test_full_name_method(self):
        """Test the 'full_name' method of the User model."""
        self.assertEqual(self.tutor.user.full_name(), "John Doe")

    def test_update_tutor(self):
        """Test that the associated User and Tutor can be updated."""
        self.user.first_name = "Jane"
        self.user.save()
        self.assertEqual(self.tutor.user.first_name, "Jane")

    def test_delete_user_deletes_tutor(self):
        """Test that deleting a User instance also deletes the associated Tutor instance."""
        self.user.delete()
        with self.assertRaises(Tutor.DoesNotExist):
            Tutor.objects.get(user=self.user)

    def test_tutor_without_user(self):
        """Ensure that creating a Tutor without a User is not allowed."""
        with self.assertRaises(IntegrityError):
            Tutor.objects.create(user=None)
