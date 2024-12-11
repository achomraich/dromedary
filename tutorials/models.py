from datetime import timedelta

from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser
from django.db import models
from libgravatar import Gravatar
from django.core.exceptions import ValidationError
from datetime import timedelta, date

from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator

# tested
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
    about_me = models.TextField(max_length=2000, blank=True, default='')

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


# tested
class Tutor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='tutor_profile')
    subjects = models.ManyToManyField('Subject', through='TaughtSubjects')
    experience = models.TextField(blank=True)

    def __str__(self):
        return self.user.full_name()

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='student_profile')
    has_new_lesson_notification = models.BooleanField(default=False)

    def __str__(self):
        return self.user.full_name()

# tested
class Admin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='admin_profile')

class Subject(models.Model):

    subject_id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=20)
    description = models.CharField(
        max_length=255,
        default=''
    )

    def __str__(self):
        return self.name

class TaughtSubjects(models.Model):
    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE)
    subject_id = models.ForeignKey(Subject, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('tutor', 'subject_id')

class Status(models.TextChoices):
    PENDING = 'Pending', 'Pending'
    BOOKED = 'Booked', 'Booked'
    CANCELLED = 'Cancelled', 'Cancelled'
    COMPLETED = 'Completed', 'Completed'

    CONFIRMED = 'Confirmed', 'Confirmed'
    REJECTED = 'Rejected', 'Rejected'


class DaysOfWeek(models.TextChoices):
    MON = 'Mon', 'Monday'
    TUE = 'Tue', 'Tuesday'
    WED = 'Wed', 'Wednesday'
    THU = 'Thu', 'Thursday'
    FRI = 'Fri', 'Friday'
    SAT = 'Sat', 'Saturday'
    SUN = 'Sun', 'Sunday'

class TutorAvailability(models.Model):
    STATUS_CHOICES = [
        ('Available', 'Available'),
        ('Booked', 'Booked'),
    ]
    id = models.BigAutoField(primary_key=True)
    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE)
    day = models.CharField(max_length=15, choices=DaysOfWeek.choices)
    start_time = models.TimeField()
    end_time = models.TimeField()
    # available or booked
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)


class Term(models.Model):
    """TERM_NAME = {
        1: "Sept-Jan",
        2: "Feb-Apr",
        3: "May_Jul"
    }"""
    term_id = models.BigAutoField(primary_key=True)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return f"{self.start_date.strftime('%b %Y')} - {self.end_date.strftime('%b %Y')}"

    def clean(self):
        if self.start_date >= self.end_date:
            raise ValidationError("The start date must be before the end date.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

#tested
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
    notes = models.CharField(max_length=50, default="—")

    def clean(self):
        """Custom validation logic for the Lesson model."""
        super().clean()
        if not isinstance(self.duration, timedelta):
            raise ValidationError("Duration must be a valid timedelta object.")


        if self.duration <= timedelta(0):
            raise ValidationError({"duration": "Duration must be a positive value."})

        if self.price_per_lesson <= 0:
            raise ValidationError({"price_per_lesson": "Price per lesson must be greater than zero."})

class LessonUpdateRequest(models.Model):
    UPDATE_CHOICES = [
        ('1', 'Change Tutor'),
        ('2', 'Change Day/Time'),
        ('3', 'Cancel Lessons'),
        ('4', 'Change Frequency'),
        ('5', 'Change Duration of the Lesson')
    ]

    MADE_BY_CHOICES = [
        ('Tutor', 'Tutor'),
        ('Student', 'Student'),
    ]

    IS_HANDLED_CHOICES = [
        ('N', 'Not done'),
        ('Y', 'Done'),
    ]

    lesson_update_id = models.BigAutoField(primary_key=True)
    lesson = models.OneToOneField(Lesson, on_delete=models.CASCADE)
    update_option = models.CharField(max_length=50, choices=UPDATE_CHOICES, default="1")
    details = models.CharField(max_length=255, default="")
    made_by = models.CharField(max_length=10, choices=MADE_BY_CHOICES, default="Tutor")
    is_handled = models.CharField(max_length=10, choices=IS_HANDLED_CHOICES, default="N")

    def __str__(self):
        return f"Update Request for Lesson {self.lesson.lesson_id} - {self.get_update_option_display()}"

#tested
class LessonStatus(models.Model):

    status_id = models.BigAutoField(primary_key=True)
    lesson_id = models.ForeignKey(Lesson, on_delete=models.CASCADE, default=0)
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.BOOKED)
    feedback = models.CharField(max_length=255, default="")
    invoiced = models.BooleanField(default=False)

    def clean(self):
        if self.date is None:
            raise ValidationError("Date cannot be null.")

        if self.date > date.today() and self.feedback != "":
            self.feedback = ""

    def save(self, *args, **kwargs):
        today = date.today()

        if self.date > today:
            self.feedback = ""

        elif self.date < today:
            if self.status == Status.PENDING:
                self.status = Status.CANCELLED
            elif self.status == Status.BOOKED:
                self.status = Status.COMPLETED

        super().save(*args, **kwargs)

'''class Booking(models.Model):
    booking_id = models.BigAutoField(primary_key=True)
    lesson_id = models.ForeignKey(Lesson.lesson_id, on_delete=models.CASCADE)
    admin_id = models.ForeignKey(PlatformAdmin.admin_id, on_delete=models.CASCADE)
    booking_date = models.DateField()'''


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

    FREQUENCY = [
        ('Weekly', 'Weekly'),
        ('Biweekly', 'Biweekly'),
    ]

    request_id = models.BigAutoField(primary_key=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    term = models.ForeignKey(Term, on_delete=models.CASCADE)
    time = models.TimeField()
    day = models.CharField(max_length=3, choices=DaysOfWeek)
    duration = models.DurationField(default=timedelta(hours=1))
    frequency = models.CharField(max_length=10, choices=FREQUENCY)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['request_id']

    @property
    def not_cancelled(self):
        return self.status != Status.CANCELLED

    @property
    def not_confirmed(self):
        return self.status != Status.CONFIRMED

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

    def mark_as_paid(self):
        self.status = 'PAID'
        self.save()
        # Update all associated lessons to mark them as invoiced
        for lesson_status in self.lessons.all():
            lesson_status.invoiced = True
            lesson_status.save()


# Changed the model name to avoid conflicts
class InvoiceLessonLink(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    lesson = models.ForeignKey('LessonStatus', on_delete=models.CASCADE)

    class Meta:
        # Add a unique constraint to prevent duplicate entries
        unique_together = ('invoice', 'lesson')

