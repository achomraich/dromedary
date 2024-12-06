
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
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('username', models.CharField(max_length=30, unique=True, validators=[django.core.validators.RegexValidator(message='Username must consist of @ followed by at least three alphanumericals', regex='^@\\w{3,}$')])),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('email', models.EmailField(max_length=254, unique=True)),
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
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('status', models.CharField(choices=[('UNPAID', 'Unpaid'), ('PAID', 'Paid'), ('OVERDUE', 'Overdue')], default='UNPAID', max_length=10)),
                ('due_date', models.DateField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Lesson',
            fields=[
                ('lesson_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('frequency', models.CharField(choices=[('D', 'day'), ('W', 'week'), ('M', 'month')], default='W', max_length=5)),
                ('duration', models.DurationField()),
                ('start_date', models.DateField()),
                ('price_per_lesson', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('subject_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=20)),
                ('description', models.CharField(default='', max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Term',
            fields=[
                ('term_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
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
            ],
        ),
        migrations.CreateModel(
            name='Tutor',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='tutor_profile', serialize=False, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(0.01)])),
                ('due_date', models.DateField()),
                ('is_paid', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invoices', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='LessonStatus',
            fields=[
                ('status_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('date', models.DateField()),
                ('time', models.TimeField()),
                ('status', models.CharField(choices=[('Pending', 'Pending'), ('Booked', 'Booked'), ('Cancelled', 'Cancelled'), ('Completed', 'Completed')], default='Booked', max_length=10)),
                ('feedback', models.CharField(max_length=255)),
                ('invoiced', models.BooleanField(default=False)),
                ('lesson_id', models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='tutorials.lesson')),
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
                ('update_option', models.CharField(choices=[('1', 'Change Tutor'), ('2', 'Change Day/Time'), ('3', 'Cancel Lessons'), ('4', 'Change Frequency'), ('5', 'Change Duration of the Lesson')], default='1', max_length=50)),
                ('details', models.CharField(default='', max_length=255)),
                ('lesson', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='tutorials.lesson')),
            ],
        ),
        migrations.AddField(
            model_name='lesson',
            name='subject_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tutorials.subject'),
        ),
        migrations.AddField(
            model_name='lesson',
            name='term_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tutorials.term'),
        ),
        migrations.CreateModel(
            name='Requests',
            fields=[
                ('request_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('status', models.CharField(choices=[('Pending', 'Pending'), ('Booked', 'Booked'), ('Cancelled', 'Cancelled'), ('Completed', 'Completed')], default='Pending', max_length=10)),
                ('lesson_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tutorials.lesson')),
                ('subject_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tutorials.subject')),
                ('student_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tutorials.student')),
            ],
        ),
        migrations.CreateModel(
            name='LessonRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language', models.CharField(choices=[('python', 'Python'), ('c++', 'C++'), ('java', 'Java')], max_length=10)),
                ('lesson_time', models.TimeField()),
                ('lesson_day', models.CharField(choices=[('mon', 'Monday'), ('tue', 'Tuesday'), ('wed', 'Wednesday'), ('thu', 'Thursday'), ('fri', 'Friday'), ('sat', 'Saturday'), ('sun', 'Sunday')], max_length=3)),
                ('lesson_length', models.IntegerField()),
                ('lesson_frequency', models.IntegerField(choices=[(1, 'Weekly'), (2, 'Biweekly')])),
                ('language', models.CharField(choices=[('c++', 'C++'), ('java', 'Java'), ('python', 'Python')], max_length=10)),
                ('lesson_time', models.TimeField()),
                ('lesson_day', models.CharField(choices=[('tue', 'Tuesday'), ('thu', 'Thursday'), ('sun', 'Sunday'), ('wed', 'Wednesday'), ('sat', 'Saturday'), ('mon', 'Monday'), ('fri', 'Friday')], max_length=9)),
                ('lesson_length', models.IntegerField()),
                ('lesson_frequency', models.CharField(choices=[(2, 'Biweekly'), (1, 'Weekly')], max_length=20)),
                ('status', models.CharField(choices=[('Pending', 'Pending'), ('Booked', 'Booked'), ('Cancelled', 'Cancelled'), ('Completed', 'Completed')], default='Pending', max_length=10)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tutorials.student')),
            ],
        ),
        migrations.AddField(
            model_name='lesson',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tutorials.student'),
        ),
        migrations.AddField(
            model_name='invoice',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='student_invoices', to='tutorials.student'),
        migrations.CreateModel(
            name='Invoices',
            fields=[
                ('invoice_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('lesson_count', models.IntegerField(default=0)),
                ('issue_date', models.DateField()),
                ('due_date', models.DateField()),
                ('total_amount', models.IntegerField()),
                ('status', models.CharField(choices=[('P', 'Paid'), ('U', 'Unpaid'), ('O', 'Overdue')], default='U', max_length=1)),
                ('lesson_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tutorials.lesson')),
                ('student_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tutorials.student')),
            ],
        ),
        migrations.CreateModel(
            name='TutorReviews',
            fields=[
                ('review_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('text', models.CharField(max_length=255)),
                ('date', models.DateField()),
                ('rating', models.CharField(choices=[(1, 'Poor'), (2, 'Fair'), (3, 'Good'), (4, 'Very Good'), (5, 'Excellent')], default=5, max_length=1)),
                ('student_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tutorials.student')),
                ('tutor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tutorials.tutor')),
            ],
        ),
        migrations.CreateModel(
            name='TutorAvailability',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('day_of_week', models.CharField(max_length=10)),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('status', models.CharField(choices=[('a', 'Available'), ('b', 'Booked')], default='a', max_length=10)),
                ('tutor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tutorials.tutor')),
            ],
        ),
        migrations.AddField(
            model_name='lesson',
            name='tutor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tutorials.tutor'),
        ),
    ]
