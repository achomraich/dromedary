from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser
from django.db import models
from libgravatar import Gravatar
from django.core.exceptions import ValidationError
from datetime import date, timedelta, datetime, time as pytime
from random import randint, choice, choices
from django.conf import settings
from django.utils import timezone
from tutorials.models.users import Tutor, TutorAvailability
from tutorials.models.shared import Subject, Term
from tutorials.models.choices import Frequency, Status, Days

class BaseLesson(models.Model):
    """Abstract model for lessons."""
    student = models.ForeignKey('Student', on_delete=models.CASCADE)
    duration = models.DurationField(default=timedelta(hours=1))
    start_date = models.DateField()

    class Meta:
        abstract = True

    def clean(self):
        """Ensures there is a start date and that the duration is positive."""
        if not self.start_date:
            raise ValidationError("Start date is required.")
        '''if self.start_date < date.today():
            raise ValidationError("Start date must be in the future.")'''
        if not isinstance(self.duration, timedelta):
            raise ValidationError("Duration must be a valid timedelta object.")

        if self.duration <= timedelta(0):
            raise ValidationError("Duration must be a positive value.")

class Lesson(BaseLesson):
    """Model for a specific lesson."""
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
        """Ensures lesson price is positive."""
        super().clean()
        if not isinstance(self.duration, timedelta):
            raise ValidationError("Duration must be a valid timedelta object.")

        if self.duration <= timedelta(0):
            raise ValidationError({"duration": "Duration must be a positive value."})

        if self.price_per_lesson is None or self.price_per_lesson <= 0:
            raise ValidationError({"price_per_lesson": "Price per lesson must be greater than zero."})

    def save(self, *args, **kwargs):
        """Creates associated lesson status and updates tutor availability."""
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if is_new:
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

                if current_date is None:
                    raise ValidationError("Due date cannot be empty.")
                
                if current_date >= today:
                    # If the date is in the future, ensure feedback is empty and status is 'Scheduled'
                    status = 'Scheduled'
                else:
                    # For past or current dates, randomize status and feedback
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

                    # Update date based on frequency
                    if self.frequency == 'O':  # Daily
                        break
                    elif self.frequency == 'W':  # Weekly
                        current_date += timedelta(weeks=1)
                    elif self.frequency == 'M':  # Monthly
                        current_date += timedelta(weeks=4)
                    elif self.frequency == 'F':  # Biweekly
                        current_date += timedelta(weeks=2)
                except Exception as e:
                    print(f"Error creating LessonStatus: {e}")

            try:
                TutorAvailability.objects.create(
                    tutor=self.tutor,
                    day=start_date.weekday(),
                    start_time=start_time,
                    end_time=end_time,
                    status=TutorAvailability.Availability.BOOKED,
                )
            except Exception as e:
                print(f"Error creating TutorAvailability: {e}")

class LessonRequest(BaseLesson):
    """Model for a request for scheduling a lesson."""
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    term = models.ForeignKey(Term, on_delete=models.CASCADE)
    time = models.TimeField()
    start_date = models.DateField()
    frequency = models.CharField(max_length=10, choices=Frequency.choices)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    created = models.DateTimeField(auto_now_add=True)
    lesson_assigned = models.ForeignKey(Lesson, on_delete=models.CASCADE, null=True, blank=True)

    def clean(self):
        """Ensures duration is positive, and the start date is positive and within the term dates."""
        if self.duration <= timedelta(0):
            raise ValidationError("Duration must be a positive value.")
        if not self.start_date:
            raise ValidationError("Start date is required.")
        if self.start_date < date.today():
            raise ValidationError("Start date must be in the future.")
        if self.start_date < self.term.start_date or self.start_date > self.term.end_date:
            print(self.start_date)

            print(self.term.start_date)
            print(self.term.end_date)
            raise ValidationError("Start date must be within the term.")

    def decided(self):
        """Check if the request has been either confirmed or cancelled."""
        return self.cancelled() or self.confirmed()

    def cancelled(self):
        """Check if the request is cancelled."""
        return self.status == Status.CANCELLED

    def confirmed(self):
        """Check if the request is confirmed."""
        return self.status == Status.CONFIRMED

class LessonUpdateRequest(models.Model):
    """Model for a request to update or modify an existing lesson."""
    class UpdateOption(models.TextChoices):
        CHANGE_TUTOR = '1', 'Change Tutor'
        CHANGE_DAY_TIME = '2', 'Change Day/Time'
        CANCEL_LESSONS = '3', 'Cancel Lessons'

    class MadeBy(models.TextChoices):
        TUTOR = 'Tutor', 'Tutor'
        STUDENT = 'Student', 'Student'

    class IsHandled(models.TextChoices):
        NOT_DONE = 'N', 'Not done'
        DONE = 'Y', 'Done'

    lesson_update_id = models.BigAutoField(primary_key=True)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    update_option = models.CharField(max_length=1, choices=UpdateOption.choices, default=UpdateOption.CHANGE_TUTOR)
    details = models.CharField(max_length=255, blank=True)
    made_by = models.CharField(max_length=10, choices=MadeBy.choices, default=MadeBy.TUTOR)
    is_handled = models.CharField(max_length=10, choices=IsHandled.choices, default=IsHandled.NOT_DONE)

class LessonStatus(models.Model):
    """Model for the status of a specific lesson, including completion, feedback, and invoicing."""
    lesson_id = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.SCHEDULED)
    feedback = models.CharField(max_length=255, blank=True)
    invoiced = models.BooleanField(default=False)

    def clean(self):
        if self.date is None:
            raise ValidationError("Due date cannot be empty.")
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
            elif self.status == Status.SCHEDULED:
                self.status = Status.COMPLETED


        if self.status != Status.COMPLETED:
            self.feedback = ''

        super().save(*args, **kwargs)
        