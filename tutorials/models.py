from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser
from django.db import models
from libgravatar import Gravatar
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator

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
    subject_id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=20)
    description = models.CharField(
        max_length=255,
        default=''
    )


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
    BOOKED = 'Booked', 'Booked'
    CANCELLED = 'Cancelled', 'Cancelled'
    COMPLETED = 'Completed', 'Completed'


class LessonUpdateRequest(models.Model):
    UPDATE_CHOICES = [
        ('1', 'Change Tutor'),
        ('2', 'Change Day/Time'),
        ('3', 'Cancel Lessons'),
        ('4', 'Change Frequency'),
        ('5', 'Change Duration of the Lesson')
    ]
    lesson_update_id = models.BigAutoField(primary_key=True)
    lesson = models.OneToOneField(Lesson, on_delete=models.CASCADE)
    update_option = models.CharField(max_length=50, choices=UPDATE_CHOICES, default="1")
    details = models.CharField(max_length=255, default="")

    def __str__(self):
        return f"Update Request for Lesson {self.lesson.lesson_id} - {self.get_update_option_display()}"


class LessonStatus(models.Model):
    # STATUS = ["Pending", "Confirmed", "Cancelled", "Completed"]

    status_id = models.BigAutoField(primary_key=True)
    lesson_id = models.ForeignKey(Lesson, on_delete=models.CASCADE, default=0)
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.BOOKED)
    feedback = models.CharField(max_length=255)
    invoiced = models.BooleanField(default=False)


'''class Booking(models.Model):
    booking_id = models.BigAutoField(primary_key=True)
    lesson_id = models.ForeignKey(Lesson.lesson_id, on_delete=models.CASCADE)
    admin_id = models.ForeignKey(PlatformAdmin.admin_id, on_delete=models.CASCADE)
    booking_date = models.DateField()'''
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


class LessonRequest(models.Model):
    LANGUAGE = [
        ('python', 'Python'),
        ('c++', 'C++'),
        ('java', 'Java'),
    ]
    DAYS = [
        ('mon', 'Monday'),
        ('tue', 'Tuesday'),
        ('wed', 'Wednesday'),
        ('thu', 'Thursday'),
        ('fri', 'Friday'),
        ('sat', 'Saturday'),
        ('sun', 'Sunday'),
    ]
    FREQUENCY = [
        (1, 'Weekly'),
        (2, 'Biweekly'),
    ]
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    language = models.CharField(max_length=10, choices=LANGUAGE)
    lesson_time = models.TimeField()
    lesson_day = models.CharField(max_length=3, choices=DAYS)
    lesson_length = models.IntegerField()
    lesson_frequency = models.IntegerField(choices=FREQUENCY)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    created = models.DateTimeField(auto_now_add=True)


class Invoice(models.Model):
    PAYMENT_STATUS = [
        ('UNPAID', 'Unpaid'),
        ('PAID', 'Paid'),
        ('OVERDUE', 'Overdue')
    ]

    id = models.AutoField(primary_key=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='student_invoices')
    lessons = models.ManyToManyField(LessonStatus, through='InvoiceLessonLink')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=PAYMENT_STATUS, default='UNPAID')
    due_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Invoice #{self.id} - {self.student.user.full_name()}"  # Changed from invoice_id to id

    def mark_as_paid(self):
        self.status = 'PAID'
        self.save()
        self.lessons.all().update(invoiced=True)

    def check_if_overdue(self):
        if self.status == 'UNPAID' and self.due_date < timezone.now().date():
            self.status = 'OVERDUE'
            self.save()

    def get_total_hours(self):
        return sum(lesson.lesson_id.duration.total_seconds() / 3600 for lesson in self.lessons.all())


# Changed the model name to avoid conflicts
class InvoiceLessonLink(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    lesson = models.ForeignKey('LessonStatus', on_delete=models.CASCADE)

    class Meta:
        # Add a unique constraint to prevent duplicate entries
        unique_together = ('invoice', 'lesson')