from django.db import models

class Status(models.TextChoices):
    PENDING = 'Pending', 'Pending'
    #BOOKED = 'Booked', 'Booked'
    SCHEDULED = 'Scheduled', 'Scheduled'
    CANCELLED = 'Cancelled', 'Cancelled'
    COMPLETED = 'Completed', 'Completed'
    CONFIRMED = 'Confirmed', 'Confirmed'
    REJECTED = 'Rejected', 'Rejected'

class Days(models.IntegerChoices):
    MON = 0, 'Monday'
    TUE = 1, 'Tuesday'
    WED = 2, 'Wednesday'
    THU = 3, 'Thursday'
    FRI = 4, 'Friday'
    SAT = 5, 'Saturday'
    SUN = 6, 'Sunday'

class Frequency(models.TextChoices):
    WEEKLY = 'W', 'Weekly'
    BIWEEKLY = 'F', 'Fortnightly'
    MONTHLY = 'M', 'Monthly'
    ONCE = 'O', 'Once'   

class PaymentStatus(models.TextChoices):
    UNPAID = 'UNPAID', 'Unpaid'
    PAID = 'PAID', 'Paid'
    OVERDUE = 'OVERDUE', 'Overdue'