from django.db import models
from django.core.exceptions import ValidationError
from datetime import date
from random import choices
from tutorials.models.users import Student
from tutorials.models.lessons import LessonStatus
from tutorials.models.invoices import PaymentStatus

class Invoice(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='invoices')
    lessons = models.ManyToManyField(LessonStatus, through='InvoiceLessonLink')
    due_date = models.DateField()
    status = models.CharField(max_length=10, choices=PaymentStatus.choices, default=PaymentStatus.UNPAID)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    amount = models.DecimalField(max_digits=6, decimal_places=2)

    def check_if_overdue(self):
        """Mark invoice as overdue if unpaid and past due date."""
        if self.status == PaymentStatus.UNPAID and self.due_date < date.today():
            if self.status != PaymentStatus.OVERDUE:
                self.status = PaymentStatus.OVERDUE
                self.save()

    def get_total_hours(self):
        """Calculate total hours for all associated lessons."""
        return sum(lesson.lesson_id.duration.total_seconds() / 3600 for lesson in self.lessons.all())

    def mark_as_paid(self):
        self.status = 'PAID'
        self.save()
        # Update all associated lessons to mark them as invoiced
        for lesson_status in self.lessons.all():
            lesson_status.invoiced = True
            lesson_status.save()

    def clean(self):
        """Shared validation logic for invoices."""
        if self.due_date < date.today():
            print("Error")
            raise ValidationError("Due date cannot be in the past.")

class InvoiceLessonLink(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    lesson = models.ForeignKey('LessonStatus', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('invoice', 'lesson')