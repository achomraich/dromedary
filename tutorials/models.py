from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser
from django.db import models
from libgravatar import Gravatar
from django.core.exceptions import ValidationError
from datetime import date, timedelta, datetime, time as pytime
from random import randint, choice, choices
from django.conf import settings
from django.utils import timezone
from .choices import Status, Days, Frequency, PaymentStatus

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

class Tutor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='tutor_profile')
    subjects = models.ManyToManyField('Subject', blank=True)
    experience = models.TextField(blank=True)

    def __str__(self):
        return self.user.full_name()

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='student_profile')
    has_new_lesson_notification = models.BooleanField(default=False)

    def __str__(self):
        return self.user.full_name()


class Admin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='admin_profile')

class Subject(models.Model):
    name = models.CharField(max_length=20)
    description = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name

class TutorAvailability(models.Model):
    class Availability(models.TextChoices):
        AVAILABLE = 'Available', 'Available'
        BOOKED = 'Unavailable', 'Unavailable'

    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE)
    day = models.IntegerField(choices=Days.choices)
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.CharField(max_length=11, choices=Availability.choices)

    class Meta:
        unique_together = ('tutor', 'day', 'start_time', 'end_time')

class TutorReview(models.Model):
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

class Term(models.Model):
    class Term(models.IntegerChoices):
        SEPT_JAN = 1, 'Sept-Jan'
        FEB_APR = 2, 'Feb-Apr'
        MAY_JUL = 3, 'May-Jul'

    start_date = models.DateField()
    end_date = models.DateField()
    term_name = models.IntegerField(choices=Term.choices, null=True, blank=True)

    def __str__(self):
        return self.get_term_name_display() if self.term_name else "Undefined Term"

    def clean(self):
        if self.start_date >= self.end_date:
            raise ValidationError("The start date must be before the end date.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

class BaseLesson(models.Model):
    student = models.ForeignKey('Student', on_delete=models.CASCADE)
    duration = models.DurationField(default=timedelta(hours=1))
    start_date = models.DateField()

    class Meta:
        abstract = True

    def clean(self):
        if not self.start_date:
            raise ValidationError("Start date is required.")
        if self.start_date < date.today():
            raise ValidationError("Start date must be in the future.")
        if self.duration <= timedelta(0):
            raise ValidationError("Duration must be a positive value.")

class Lesson(BaseLesson):
    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    term = models.ForeignKey(Term, on_delete=models.CASCADE)
    frequency = models.CharField(max_length=5, choices=Frequency.choices)
    set_start_time = models.TimeField(null=True, blank=True)
    price_per_lesson = models.DecimalField(max_digits=6, decimal_places=2)
    notes = models.CharField(max_length=50, blank=True)

    class Meta:
        unique_together = ('tutor', 'student', 'subject_id')

    def clean(self):
        """Custom validation logic for the Lesson model."""
        super().clean()
        if not isinstance(self.duration, timedelta):
            raise ValidationError("Duration must be a valid timedelta object.")

        if self.duration <= timedelta(0):
            raise ValidationError({"duration": "Duration must be a positive value."})

        if self.price_per_lesson is None or self.price_per_lesson <= 0:
            raise ValidationError({"price_per_lesson": "Price per lesson must be greater than zero."})

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if is_new:
            print("New Lesson detected")
            term = self.term
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
                    print("LessonStatus created")
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
                print("TutorAvailability created")
            except Exception as e:
                print(f"Error creating TutorAvailability: {e}")

class LessonRequest(BaseLesson):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    term = models.ForeignKey(Term, on_delete=models.CASCADE)
    time = models.TimeField()
    start_date = models.DateField()
    frequency = models.CharField(max_length=10, choices=Frequency.choices)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    created = models.DateTimeField(auto_now_add=True)
    lesson_assigned = models.ForeignKey(Lesson, on_delete=models.CASCADE, null=True, blank=True)

    def clean(self):
        if not self.start_date:
            raise ValidationError("Start date is required.")
        if self.start_date < date.today():
            raise ValidationError("Start date must be in the future.")
        if self.start_date < self.term.start_date or self.start_date > self.term.end_date:
            raise ValidationError("Start date must be within the term.")
        if self.duration <= timedelta(0):
            raise ValidationError("Duration must be a positive value.")

    def decided(self):
        return self.cancelled() or self.confirmed()

    def cancelled(self):
        return self.status == Status.CANCELLED

    def confirmed(self):
        return self.status == Status.CONFIRMED

class LessonUpdateRequest(models.Model):
    class UpdateOption(models.TextChoices):
        CHANGE_TUTOR = '1', 'Change Tutor'
        CHANGE_DAY_TIME = '2', 'Change Day/Time'
        CANCEL_LESSONS = '3', 'Cancel Lessons'
        CHANGE_FREQUENCY = '4', 'Change Frequency'
        CHANGE_DURATION = '5', 'Change Duration of the Lesson'

    class MadeBy(models.TextChoices):
        TUTOR = 'Tutor', 'Tutor'
        STUDENT = 'Student', 'Student'

    class IsHandled(models.TextChoices):
        NOT_DONE = 'N', 'Not done'
        DONE = 'Y', 'Done'

    lesson_update_id = models.BigAutoField(primary_key=True)
    lesson = models.OneToOneField(Lesson, on_delete=models.CASCADE)
    update_option = models.CharField(max_length=1, choices=UpdateOption.choices, default=UpdateOption.CHANGE_TUTOR)
    details = models.CharField(max_length=255, blank=True)
    made_by = models.CharField(max_length=10, choices=MadeBy.choices, default=MadeBy.TUTOR)
    is_handled = models.CharField(max_length=10, choices=IsHandled.choices, default=IsHandled.NOT_DONE)

class LessonStatus(models.Model):
    lesson_id = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.BOOKED)
    feedback = models.CharField(max_length=255, blank=True)
    invoiced = models.BooleanField(default=False)

    def clean(self):
        if self.date > date.today() and self.feedback != "":
            raise ValidationError("Feedback should be empty for future lessons.")

        if not self.date:
            raise ValidationError("Date cannot be null.")

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

class BaseInvoice(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='invoices')
    due_date = models.DateField()
    status = models.CharField(max_length=10, choices=PaymentStatus.choices, default=PaymentStatus.UNPAID)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    amount = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        abstract = True

    def check_if_overdue(self):
        """Mark invoice as overdue if unpaid and past due date."""
        if self.status == PaymentStatus.UNPAID and self.due_date < date.today():
            if self.status != PaymentStatus.OVERDUE:
                self.status = PaymentStatus.OVERDUE
                self.save()

    def clean(self):
        """Shared validation logic for invoices."""
        if self.due_date < date.today():
            print("Error")
            raise ValidationError("Due date cannot be in the past.")

class Invoice(BaseInvoice):
    lessons = models.ManyToManyField(LessonStatus, through='InvoiceLessonLink')

    def mark_as_paid(self):
        """Mark the invoice as paid and update associated lessons."""
        if self.status != 'PAID':
            self.status = 'PAID'
            self.save()
            self.lessons.all().update(invoiced=True)

    def get_total_hours(self):
        """Calculate total hours for all associated lessons."""
        return sum(lesson.lesson_id.duration.total_seconds() / 3600 for lesson in self.lessons.all())

class Invoices(models.Model):
    lesson_count = models.IntegerField(default=0)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)

class InvoiceLessonLink(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    lesson = models.ForeignKey('LessonStatus', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('invoice', 'lesson')
