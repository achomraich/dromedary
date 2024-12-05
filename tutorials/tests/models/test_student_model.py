from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from tutorials.models import Student, User


class StudentModelTest(TestCase):

    def setUp(self):

        self.user = User.objects.create_user(
            username="@student1",
            first_name="John",
            last_name="Doe",
            email="johndoe@example.com",
            password="Password123"
        )

        self.student = Student.objects.create(user=self.user)

    def test_valid_student_is_valid(self):
        try:
            self.student.full_clean()
        except ValidationError:
            self.fail("Default test student should be deemed valid!")

    def test_student_creation(self):
        self.assertEqual(self.student.user, self.user)
        self.assertEqual(self.student.user.first_name, "John")
        self.assertEqual(self.student.user.last_name, "Doe")

    def test_full_name_method(self):
        """Test the 'full_name' method of the User model."""
        self.assertEqual(self.student.user.full_name(), "John Doe")

    def test_update_student(self):
        """Test that the associated User and Student can be updated."""
        self.user.first_name = "Jane"
        self.user.save()
        self.assertEqual(self.student.user.first_name, "Jane")

    def test_delete_user_deletes_student(self):
        """Test that deleting a User instance also deletes the associated Student instance."""
        self.user.delete()
        with self.assertRaises(Student.DoesNotExist):
            Student.objects.get(user=self.user)

    def test_student_without_user(self):
        """Ensure that creating a Student without a User is not allowed."""
        with self.assertRaises(IntegrityError):
            Student.objects.create(user=None)
