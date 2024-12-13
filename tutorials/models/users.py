from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser
from django.db import models
from libgravatar import Gravatar
from tutorials.models.choices import Days

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
    about_me = models.TextField(max_length=2000, blank=True, default='')

    class Meta:
        """Model options."""
        ordering = ['last_name', 'first_name']

    def full_name(self):
        """Return a string containing the user's full name."""
        return f'{self.first_name} {self.last_name}'

    def __str__(self):
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
    
class Admin(models.Model):
    """Model for admin users."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='admin_profile')

class Student(models.Model):
    """Model for student users."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='student_profile')
    has_new_lesson_notification = models.BooleanField(default=False)

    def __str__(self):
        return self.user.full_name()

class Tutor(models.Model):
    """Model for tutor users."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='tutor_profile')
    subjects = models.ManyToManyField('Subject', blank=True)
    experience = models.TextField(blank=True)

    def __str__(self):
        return self.user.full_name()

class TutorAvailability(models.Model):
    """Model for the availability schedule of a tutor."""
    class Availability(models.TextChoices):
        AVAILABLE = 'Available', 'Available'
        BOOKED = 'Unavailable', 'Unavailable'

    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE)
    day = models.IntegerField(choices=Days.choices)
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.CharField(max_length=11, choices=Availability.choices)

    class Meta:
        """Ensures unique availability entries for a tutor per day and time slot."""
        unique_together = ('tutor', 'day', 'start_time', 'end_time')
        
    def __str__(self):
        return f"{self.tutor.user.full_name()} - {self.get_day_display()} - {self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')} ({self.get_status_display()})"

class TutorReview(models.Model):
    """Model for a review left by a student for a tutor."""
    class Rating(models.TextChoices):
        POOR = '1', 'Poor'
        FAIR = '2', 'Fair'
        GOOD = '3', 'Good'
        VERY_GOOD = '4', 'Very Good'
        EXCELLENT = '5', 'Excellent'

    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    date = models.DateField()
    rating = models.CharField(max_length=1, choices=Rating.choices, default=Rating.EXCELLENT)
