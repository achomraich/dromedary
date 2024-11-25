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