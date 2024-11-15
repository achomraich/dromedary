

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tutorials", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(

            name="Admin",
            fields=[
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        primary_key=True,
                        related_name="admin_profile",
                        serialize=False,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Lesson",
            fields=[
                ("lesson_id", models.BigAutoField(primary_key=True, serialize=False)),
                (
                    "frequency",
                    models.CharField(
                        choices=[("D", "day"), ("W", "week"), ("M", "month")],
                        default="W",
                        max_length=5,
                    ),
                ),
                ("duration", models.DurationField()),
                ("start_date", models.DateField()),
                ("price_per_lesson", models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name="Student",
            fields=[
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        primary_key=True,
                        related_name="student_profile",
                        serialize=False,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Subject",
            fields=[
                ("subject_id", models.BigAutoField(primary_key=True, serialize=False)),
                (
                    "name",
                    models.CharField(
                        choices=[
                            ("Python", "Course description"),
                            ("C++", "Course description"),
                            ("JS", "Course description"),
                            ("TypeScript", "Course description"),
                            ("Scala", "Course description"),
                            ("Ruby", "Course description"),
                        ],
                        max_length=20,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Term",
            fields=[
                ("term_id", models.BigAutoField(primary_key=True, serialize=False)),
                ("start_date", models.DateField()),
                ("end_date", models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name="Tutor",
            fields=[
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        primary_key=True,
                        related_name="tutor_profile",
                        serialize=False,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.AlterField(
            model_name="user",
            name="id",
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
        migrations.CreateModel(
            name="LessonStatus",
            fields=[
                ("status_id", models.BigAutoField(primary_key=True, serialize=False)),
                ("date", models.DateField()),
                ("time", models.TimeField()),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("Pending", "Pending"),
                            ("Confirmed", "Confirmed"),
                            ("Cancelled", "Cancelled"),
                            ("Completed", "Completed"),
                        ],
                        default="Pending",
                        max_length=10,
                    ),
                ),
                ("feedback", models.CharField(max_length=255)),
                ("invoiced", models.BooleanField(default=False)),
                (
                    "lesson_id",
                    models.ForeignKey(
                        default=0,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="tutorials.lesson",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="lesson",
            name="student",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="tutorials.student"
            ),
        ),
        migrations.CreateModel(
            name="Invoices",
            fields=[
                ("invoice_id", models.BigAutoField(primary_key=True, serialize=False)),
                ("lesson_count", models.IntegerField(default=0)),
                ("issue_date", models.DateField()),
                ("due_date", models.DateField()),
                ("total_amount", models.IntegerField()),
                (
                    "status",
                    models.CharField(
                        choices=[("P", "Paid"), ("U", "Unpaid"), ("O", "Overdue")],
                        default="U",
                        max_length=1,
                    ),
                ),
                (
                    "lesson_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="tutorials.lesson",
                    ),
                ),
                (
                    "student_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="tutorials.student",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Requests",
            fields=[
                ("request_id", models.BigAutoField(primary_key=True, serialize=False)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("Pending", "Pending"),
                            ("Confirmed", "Confirmed"),
                            ("Cancelled", "Cancelled"),
                            ("Completed", "Completed"),
                        ],
                        default="Pending",
                        max_length=10,
                    ),
                ),
                (
                    "lesson_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="tutorials.lesson",
                    ),
                ),
                (
                    "student_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="tutorials.student",
                    ),
                ),
                (
                    "subject_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="tutorials.subject",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="lesson",
            name="subject_id",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="tutorials.subject"
            ),
        ),
        migrations.AddField(
            model_name="lesson",
            name="term_id",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="tutorials.term"
            ),
        ),
        migrations.AddField(
            model_name="lesson",
            name="tutor",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="tutorials.tutor"
            ),
        ),
        migrations.CreateModel(
            name="TutorAvailability",
            fields=[
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                ("day_of_week", models.CharField(max_length=10)),
                ("start_time", models.TimeField()),
                ("end_time", models.TimeField()),
                (
                    "status",
                    models.CharField(
                        choices=[("a", "Available"), ("b", "Booked")],
                        default="a",
                        max_length=10,
                    ),
                ),
                (
                    "tutor",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="tutorials.tutor",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="TutorReviews",
            fields=[
                ("review_id", models.BigAutoField(primary_key=True, serialize=False)),
                ("text", models.CharField(max_length=255)),
                ("date", models.DateField()),
                (
                    "rating",
                    models.CharField(
                        choices=[
                            (1, "Poor"),
                            (2, "Fair"),
                            (3, "Good"),
                            (4, "Very Good"),
                            (5, "Excellent"),
                        ],
                        default=5,
                        max_length=1,
                    ),
                ),
                (
                    "student_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="tutorials.student",
                    ),
                ),
                (
                    "tutor",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="tutorials.tutor",
                    ),
                ),
            ],
        ),
    ]
