# Generated by Django 5.1.2 on 2024-12-13 12:21

import datetime
import django.contrib.auth.models
import django.core.validators
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('username', models.CharField(max_length=30, unique=True, validators=[django.core.validators.RegexValidator(message='Username must consist of @ followed by at least three alphanumericals', regex='^@\\w{3,}$')])),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('about_me', models.TextField(blank=True, default='', max_length=2000)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'ordering': ['last_name', 'first_name'],
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('due_date', models.DateField()),
                ('status', models.CharField(choices=[('UNPAID', 'Unpaid'), ('PAID', 'Paid'), ('OVERDUE', 'Overdue')], default='UNPAID', max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=6)),
            ],
        ),
        migrations.CreateModel(
            name='Lesson',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('duration', models.DurationField(default=datetime.timedelta(seconds=3600))),
                ('start_date', models.DateField()),
                ('frequency', models.CharField(choices=[('W', 'Weekly'), ('F', 'Fortnightly'), ('M', 'Monthly'), ('O', 'Once')], max_length=5)),
                ('set_start_time', models.TimeField(blank=True, null=True)),
                ('price_per_lesson', models.DecimalField(decimal_places=2, max_digits=6)),
                ('notes', models.CharField(blank=True, max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
                ('description', models.CharField(blank=True, max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Term',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('term_name', models.IntegerField(blank=True, choices=[(1, 'Sept-Jan'), (2, 'Feb-Apr'), (3, 'May-Jul')], null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Admin',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='admin_profile', serialize=False, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='student_profile', serialize=False, to=settings.AUTH_USER_MODEL)),
                ('has_new_lesson_notification', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Tutor',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='tutor_profile', serialize=False, to=settings.AUTH_USER_MODEL)),
                ('experience', models.TextField(blank=True)),
                ('subjects', models.ManyToManyField(blank=True, to='tutorials.subject')),
            ],
        ),
        migrations.CreateModel(
            name='LessonStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('time', models.TimeField()),
                ('status', models.CharField(choices=[('Pending', 'Pending'), ('Scheduled', 'Scheduled'), ('Cancelled', 'Cancelled'), ('Completed', 'Completed'), ('Confirmed', 'Confirmed'), ('Rejected', 'Rejected')], default='Scheduled', max_length=10)),
                ('feedback', models.CharField(blank=True, max_length=255)),
                ('invoiced', models.BooleanField(default=False)),
                ('lesson_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tutorials.lesson')),
            ],
        ),
        migrations.CreateModel(
            name='InvoiceLessonLink',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('invoice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tutorials.invoice')),
                ('lesson', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tutorials.lessonstatus')),
            ],
            options={
                'unique_together': {('invoice', 'lesson')},
            },
        ),
        migrations.AddField(
            model_name='invoice',
            name='lessons',
            field=models.ManyToManyField(through='tutorials.InvoiceLessonLink', to='tutorials.lessonstatus'),
        ),
        migrations.CreateModel(
            name='LessonUpdateRequest',
            fields=[
                ('lesson_update_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('update_option', models.CharField(choices=[('1', 'Change Tutor'), ('2', 'Change Day/Time'), ('3', 'Cancel Lessons')], default='1', max_length=1)),
                ('details', models.CharField(blank=True, max_length=255)),
                ('made_by', models.CharField(choices=[('Tutor', 'Tutor'), ('Student', 'Student')], default='Tutor', max_length=10)),
                ('is_handled', models.CharField(choices=[('N', 'Not done'), ('Y', 'Done')], default='N', max_length=10)),
                ('lesson', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tutorials.lesson')),
            ],
        ),
        migrations.AddField(
            model_name='lesson',
            name='subject',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tutorials.subject'),
        ),
        migrations.AddField(
            model_name='lesson',
            name='term',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tutorials.term'),
        ),
        migrations.CreateModel(
            name='LessonRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('duration', models.DurationField(default=datetime.timedelta(seconds=3600))),
                ('time', models.TimeField()),
                ('start_date', models.DateField()),
                ('frequency', models.CharField(choices=[('W', 'Weekly'), ('F', 'Fortnightly'), ('M', 'Monthly'), ('O', 'Once')], max_length=10)),
                ('status', models.CharField(choices=[('Pending', 'Pending'), ('Scheduled', 'Scheduled'), ('Cancelled', 'Cancelled'), ('Completed', 'Completed'), ('Confirmed', 'Confirmed'), ('Rejected', 'Rejected')], default='Pending', max_length=10)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('lesson_assigned', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='tutorials.lesson')),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tutorials.subject')),
                ('term', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tutorials.term')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tutorials.student')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='lesson',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tutorials.student'),
        ),
        migrations.AddField(
            model_name='invoice',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invoices', to='tutorials.student'),
        ),
        migrations.CreateModel(
            name='TutorReview',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=255)),
                ('date', models.DateField()),
                ('rating', models.CharField(choices=[('1', 'Poor'), ('2', 'Fair'), ('3', 'Good'), ('4', 'Very Good'), ('5', 'Excellent')], default='5', max_length=1)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tutorials.student')),
                ('tutor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tutorials.tutor')),
            ],
        ),
        migrations.AddField(
            model_name='lesson',
            name='tutor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tutorials.tutor'),
        ),
        migrations.CreateModel(
            name='TutorAvailability',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day', models.IntegerField(choices=[(0, 'Monday'), (1, 'Tuesday'), (2, 'Wednesday'), (3, 'Thursday'), (4, 'Friday'), (5, 'Saturday'), (6, 'Sunday')])),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('status', models.CharField(choices=[('Available', 'Available'), ('Unavailable', 'Unavailable')], max_length=11)),
                ('tutor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tutorials.tutor')),
            ],
            options={
                'unique_together': {('tutor', 'day', 'start_time', 'end_time')},
            },
        ),
        migrations.AlterUniqueTogether(
            name='lesson',
            unique_together={('tutor', 'student', 'subject_id')},
        ),
    ]
