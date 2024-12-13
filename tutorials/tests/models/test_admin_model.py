from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from tutorials.models import Admin, User

class AdminModelTest(TestCase):

    def setUp(self):

        self.user = User.objects.create_user(
            username="@admin1",
            first_name="John",
            last_name="Doe",
            email="johndoe@example.com",
            password="Password123"
        )

        self.admin = Admin.objects.create(user=self.user)

    def test_valid_admin_is_valid(self):
        try:
            self.admin.full_clean()
        except ValidationError:
            self.fail("Default test admin should be deemed valid!")

    def test_admin_creation(self):
        self.assertEqual(self.admin.user, self.user)
        self.assertEqual(self.admin.user.first_name, "John")
        self.assertEqual(self.admin.user.last_name, "Doe")

    def test_full_name_method(self):
        self.assertEqual(self.admin.user.full_name(), "John Doe")

    def test_update_admin(self):
        self.user.first_name = "Jane"
        self.user.save()
        self.assertEqual(self.admin.user.first_name, "Jane")

    def test_delete_user_deletes_admin(self):
        self.user.delete()
        with self.assertRaises(Admin.DoesNotExist):
            Admin.objects.get(user__username="@admin1")

    def test_admin_without_user(self):
        with self.assertRaises(IntegrityError):
            Admin.objects.create(user=None)
