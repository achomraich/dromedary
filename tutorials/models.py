from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser
from django.db import models
from libgravatar import Gravatar

from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator

class User(AbstractUser):
    """Model used for user authentication, and team member related information."""

    username = models.CharField(
        max_length=30,
        unique=True,
        validators=[RegexValidator(
            regex=r'^@\w{3,}$',
            message='Username must consist of @ followed by at least three alphanumericals'
        )]
    )
    first_name = models.CharField(max_length=50, blank=False)
    last_name = models.CharField(max_length=50, blank=False)
    email = models.EmailField(unique=True, blank=False)


    class Meta:
        """Model options."""

        ordering = ['last_name', 'first_name']

    def full_name(self):
        """Return a string containing the user's full name."""

        return f'{self.first_name} {self.last_name}'

    def gravatar(self, size=120):
        """Return a URL to the user's gravatar."""

        gravatar_object = Gravatar(self.email)
        gravatar_url = gravatar_object.get_image(size=size, default='mp')
        return gravatar_url

    def mini_gravatar(self):
        """Return a URL to a miniature version of the user's gravatar."""
        
        return self.gravatar(size=60)

class Invoice(models.Model):
        # Reference to the student (user) who is receiving the invoice
        student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='invoices')

        # Invoice amount with a minimum value validator to ensure it is positive number
        amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])

        # Due date for the payment
        due_date = models.DateField()

        # Payment status, marking whether the invoice has been paid
        is_paid = models.BooleanField(default=False)

        # Timestamp for when the invoice was created and last updated
        created_at = models.DateTimeField(auto_now_add=True)
        updated_at = models.DateTimeField(auto_now=True)

        def __str__(self):
            # Representation of the invoice in admin or shell views
            return f"Invoice for {self.student.username} - Amount: {self.amount}"

        def is_overdue(self):
            # Helper method to check if the invoice is overdue
            return not self.is_paid and self.due_date < timezone.now().date()