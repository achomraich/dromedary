from django.db import models
from django.core.exceptions import ValidationError

class Subject(models.Model):
    name = models.CharField(max_length=20)
    description = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name

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
