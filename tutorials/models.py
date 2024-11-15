from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser
from django.db import models
from libgravatar import Gravatar

class User(AbstractUser):
    """Model used for user authentication, and team member related information."""
    id = models.BigAutoField(primary_key=True)
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


class Tutor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='tutor_profile')


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='student_profile')


class Admin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='admin_profile')


class TutorAvailability(models.Model):
    STATUS_CHOICES = [
        ('a', 'Available'),
        ('b', 'Booked'),
    ]
    id = models.BigAutoField(primary_key=True)
    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE)
    day_of_week = models.CharField(max_length=10)
    start_time = models.TimeField()
    end_time = models.TimeField()
    # available or booked
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='a')


class Subject(models.Model):
    # SUBJECT = ["Python", "C++", "JS", "TypeScript", "Scala", "Ruby"]
    SUBJECT_CHOICES = [
        ('Python', 'Course description'),
        ('C++', 'Course description'),
        ('JS', 'Course description'),
        ('TypeScript', 'Course description'),
        ('Scala', 'Course description'),
        ('Ruby', 'Course description'),
    ]
    subject_id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=20, choices=SUBJECT_CHOICES)
    # description = models.CharField()


class Term(models.Model):
    """TERM_NAME = {
        1: "Sept-Jan",
        2: "Feb-Apr",
        3: "May_Jul"
    }"""
    term_id = models.BigAutoField(primary_key=True)
    start_date = models.DateField()
    end_date = models.DateField()


class Lesson(models.Model):
    LESSON_FREQUENCY = [
        ("D", "day"),
        ("W", "week"),
        ("M", "month")
    ]

    lesson_id = models.BigAutoField(primary_key=True)
    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject_id = models.ForeignKey(Subject, on_delete=models.CASCADE)
    term_id = models.ForeignKey(Term, on_delete=models.CASCADE)

    frequency = models.CharField(max_length=5, choices=LESSON_FREQUENCY, default="W")
    duration = models.DurationField()
    start_date = models.DateField()
    price_per_lesson = models.IntegerField()

class Status(models.TextChoices):
    PENDING = 'Pending', 'Pending'
    CONFIRMED = 'Confirmed', 'Confirmed'
    CANCELLED = 'Cancelled', 'Cancelled'
    COMPLETED = 'Completed', 'Completed'


class LessonStatus(models.Model):
    # STATUS = ["Pending", "Confirmed", "Cancelled", "Completed"]

    status_id = models.BigAutoField(primary_key=True)
    lesson_id = models.ForeignKey(Lesson, on_delete=models.CASCADE, default=0)
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING)
    feedback = models.CharField(max_length=255)
    invoiced = models.BooleanField(default=False)

'''class Booking(models.Model):
    booking_id = models.BigAutoField(primary_key=True)
    lesson_id = models.ForeignKey(Lesson.lesson_id, on_delete=models.CASCADE)
    admin_id = models.ForeignKey(PlatformAdmin.admin_id, on_delete=models.CASCADE)
    booking_date = models.DateField()'''

class Invoices(models.Model):
    PAYMENT_CHOICES = [
        ("P", "Paid"),
        ("U", "Unpaid"),
        ("O", "Overdue")
    ]
    invoice_id = models.BigAutoField(primary_key=True)
    lesson_count = models.IntegerField(default=0)
    lesson_id = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    student_id = models.ForeignKey(Student, on_delete=models.CASCADE)
    issue_date = models.DateField()
    due_date = models.DateField()
    total_amount = models.IntegerField()
    status = models.CharField(max_length=1, choices=PAYMENT_CHOICES, default="U")


class Requests(models.Model):
    # STATUS = ["Pending", "Confirmed", "Cancelled", "Completed"]
    request_id = models.BigAutoField(primary_key=True)
    student_id = models.ForeignKey(Student, on_delete=models.CASCADE)
    lesson_id = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    subject_id = models.ForeignKey(Subject, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING)



class TutorReviews(models.Model):
    RATING_CHOICES = [
        (1, 'Poor'),
        (2, 'Fair'),
        (3, 'Good'),
        (4, 'Very Good'),
        (5, 'Excellent'),
    ]

    review_id = models.BigAutoField(primary_key=True)
    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE)
    student_id = models.ForeignKey(Student, on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    date = models.DateField()
    rating = models.CharField(max_length=1, choices=RATING_CHOICES, default=5)
    
class LessonRequest(models.model):
    lesson_id = models.AutoField(primary_key=True)
    SUBJECTS = {
        'Python',
        'C++',
        'Java',
    }
    subject = models.CharField(max_length=10, choices=SUBJECTS)
    lesson_time = models.TimeField()
    DAYS = {
        'Monday',
        'Tuesday',
        'Wednesday',
        'Thursday',
        'Friday',
        'Saturday',
        'Sunday',
    }
    lesson_day = models.Charfield(max_length=9, choices=DAYS)
    lesson_length = models.IntegerField()
