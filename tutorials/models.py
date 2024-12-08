from datetime import timedelta

from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser
from django.db import models
from libgravatar import Gravatar
from django.core.exceptions import ValidationError
from datetime import date, timedelta, datetime, time as pytime
from random import randint, choice, choices


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

class Subject(models.Model):

    subject_id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=20)
    description = models.CharField(
        max_length=255,
        default=''
    )

    def __str__(self):
        return self.name

# tested
class Tutor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='tutor_profile')
    subjects = models.ManyToManyField(Subject, blank=True)
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

class Status(models.TextChoices):
    PENDING = 'Pending', 'Pending'
    BOOKED = 'Booked', 'Booked'
    CANCELLED = 'Cancelled', 'Cancelled'
    COMPLETED = 'Completed', 'Completed'
    CONFIRMED = 'Confirmed', 'Confirmed'
    REJECTED = 'Rejected', 'Rejected'

class Frequency(models.TextChoices):
    WEEKLY = 'W', 'Weekly'
    BIWEEKLY = 'B', 'Biweekly'
    MONTHLY = 'M', 'Monthly'
    ONCE = 'O', 'Once'

class DaysOfWeek(models.IntegerChoices):
    MON = 0, 'Monday'
    TUE = 1, 'Tuesday'
    WED = 2, 'Wednesday'
    THU = 3, 'Thursday'
    FRI = 4, 'Friday'
    SAT = 5, 'Saturday'
    SUN = 6, 'Sunday'

class TutorAvailability(models.Model):
    STATUS_CHOICES = [
        ('Available', 'Available'),
        ('Booked', 'Booked'),
    ]
    id = models.BigAutoField(primary_key=True)
    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE)
    day = models.IntegerField(choices=DaysOfWeek.choices)
    start_time = models.TimeField()
    end_time = models.TimeField()
    # Mark as Available or Booked
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)

    class Meta:
        unique_together = ('tutor', 'day', 'start_time', 'end_time')

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

    lesson_id = models.BigAutoField(primary_key=True)
    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject_id = models.ForeignKey(Subject, on_delete=models.CASCADE)
    term_id = models.ForeignKey(Term, on_delete=models.CASCADE)
    frequency = models.CharField(max_length=10, choices=Frequency.choices)
    duration = models.DurationField()
    set_start_time = models.TimeField(null=True, blank=True)
    start_date = models.DateField()
    price_per_lesson = models.IntegerField()
    notes = models.CharField(max_length=50, default="—")

    class Meta:
        unique_together = ('tutor', 'student', 'subject_id')

    def clean(self):
        """Custom validation logic for the Lesson model."""
        super().clean()
        if not isinstance(self.duration, timedelta):
            raise ValidationError("Duration must be a valid timedelta object.")

        if self.duration <= timedelta(0):
            raise ValidationError({"duration": "Duration must be a positive value."})

        if self.price_per_lesson <= 0:
            raise ValidationError({"price_per_lesson": "Price per lesson must be greater than zero."})

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if is_new:
            term = self.term_id
            times = [
                pytime(hour=h, minute=m)
                for h in range(9, 19)
                for m in (0, 30)
            ]
            if self.set_start_time is not None:
                times = [self.set_start_time]
            start_time = choice(times)
            start_datetime = datetime.combine(date.today(), start_time)
            end_datetime = start_datetime + self.duration
            end_time = end_datetime.time()

            today = date.today()

            start_date = term.start_date
            end_date = term.end_date

            start_date += timedelta(days=randint(0, 6))

            current_date = start_date
            while current_date <= end_date:
                if current_date >= today:
                    status = 'Scheduled'
                else:
                    status = choices(['Completed', 'Cancelled'], weights=[0.8, 0.2], k=1)[0]

                if status == 'Completed':
                    feedback = choice(['Good progress', 'Needs improvement', 'Excellent'])
                elif status == 'Cancelled':
                    feedback = '-'
                else:
                    feedback = ''
                try:
                    LessonStatus.objects.create(
                        lesson_id=self,
                        date=current_date,
                        time=start_time,
                        status=status,
                        feedback=feedback,
                        invoiced=False,
                    )
                except Exception as e:
                    print(f"Error creating LessonStatus: {e}")

                current_date += timedelta(weeks=1)

            try:
                TutorAvailability.objects.create(
                    tutor=self.tutor,
                    day=start_date.weekday(),
                    start_time=start_time,
                    end_time=end_time,
                    status='Booked',
                )
            except Exception as e:
                print(f"Error creating TutorAvailability: {e}")


class LessonRequest(models.Model):

    request_id = models.BigAutoField(primary_key=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    term = models.ForeignKey(Term, on_delete=models.CASCADE)
    time = models.TimeField()
    start_date = models.DateField()
    duration = models.DurationField(default=timedelta(hours=1))
    frequency = models.CharField(max_length=10, choices=Frequency.choices)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    created = models.DateTimeField(auto_now_add=True)

    lesson_assigned = models.ForeignKey(Lesson, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        unique_together = ['request_id']

    def clean(self):
        if not self.start_date:
            raise ValidationError("Start date is required.")
        if self.start_date < date.today():
            raise ValidationError("Start date must be in the future.")

        if self.start_date < self.term.start_date or self.start_date > self.term.end_date:
            raise ValidationError("Start date must be within the term.")

        if self.duration <= timedelta(0):
            raise ValidationError("Duration must be a positive value.")

    @property
    def decided(self):
        return not (self.not_cancelled and self.not_confirmed)

    @property
    def not_cancelled(self):
        return self.status != Status.CANCELLED

    @property
    def not_confirmed(self):
        return self.status != Status.CONFIRMED


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


