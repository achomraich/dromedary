"""Forms for the tutorials app."""
from django import forms
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from .models import User, Tutor, Student, Subject, LessonStatus, LessonUpdateRequest

class LogInForm(forms.Form):
    """Form enabling registered users to log in."""

    username = forms.CharField(label="Username")
    password = forms.CharField(label="Password", widget=forms.PasswordInput())

    def get_user(self):
        """Returns authenticated user if possible."""

        user = None
        if self.is_valid():
            username = self.cleaned_data.get('username')
            password = self.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
        return user


class UserForm(forms.ModelForm):
    """Form to update user profiles."""

    class Meta:
        """Form options."""

        model = User
        fields = ['first_name', 'last_name', 'username', 'email']

class NewPasswordMixin(forms.Form):
    """Form mixing for new_password and password_confirmation fields."""

    new_password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(),
        validators=[RegexValidator(
            regex=r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).*$',
            message='Password must contain an uppercase character, a lowercase '
                    'character and a number'
            )]
    )
    password_confirmation = forms.CharField(label='Password confirmation', widget=forms.PasswordInput())

    def clean(self):
        """Form mixing for new_password and password_confirmation fields."""

        super().clean()
        new_password = self.cleaned_data.get('new_password')
        password_confirmation = self.cleaned_data.get('password_confirmation')
        if new_password != password_confirmation:
            self.add_error('password_confirmation', 'Confirmation does not match password.')


class PasswordForm(NewPasswordMixin):
    """Form enabling users to change their password."""

    password = forms.CharField(label='Current password', widget=forms.PasswordInput())

    def __init__(self, user=None, **kwargs):
        """Construct new form instance with a user instance."""
        
        super().__init__(**kwargs)
        self.user = user

    def clean(self):
        """Clean the data and generate messages for any errors."""

        super().clean()
        password = self.cleaned_data.get('password')
        if self.user is not None:
            user = authenticate(username=self.user.username, password=password)
        else:
            user = None
        if user is None:
            self.add_error('password', "Password is invalid")

    def save(self):
        """Save the user's new password."""

        new_password = self.cleaned_data['new_password']
        if self.user is not None:
            self.user.set_password(new_password)
            self.user.save()
        return self.user


class SignUpForm(NewPasswordMixin, forms.ModelForm):
    """Form enabling unregistered users to sign up."""

    role = forms.ChoiceField(choices=[('Tutor', 'Tutor'), ('Student', 'Student')])

    class Meta:
        """Form options."""

        model = User
        fields = ['first_name', 'last_name', 'username', 'email']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("This email is already in use.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError("This username is already in use.")
        return username

    def save(self):
        """Create a new user."""

        user = User(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name']
        )
        user.set_password(self.cleaned_data['new_password'])
        user.save()

        role = self.cleaned_data.get('role')
        if role == 'Tutor':
            Tutor.objects.create(user=user)
        elif role == 'Student':
            Student.objects.create(user=user)

        return user

class SubjectForm(forms.ModelForm):

    class Meta:

        model = Subject
        fields = ['name', 'description']

    def __init__(self, *args, **kwargs):
        subject = kwargs.get('instance', None)

        super().__init__(*args, **kwargs)

        if subject and subject.pk:
            self.fields['name'].disabled = True
        else:
            self.fields['name'].disabled = False


class LessonFeedbackForm(forms.ModelForm):
    lesson_name = forms.CharField(label='Lesson Subject', required=False, disabled=True)
    student_name = forms.CharField(label='Student', required=False, disabled=True)
    lesson_date = forms.DateField(label='Lesson Date', required=False, disabled=True)
    lesson_time = forms.TimeField(label='Lesson Time', required=False, disabled=True)

    class Meta:
        model = LessonStatus
        fields = ['feedback']

    def __init__(self, *args, **kwargs):
        lesson_status = kwargs.get('instance')
        if lesson_status:
            lesson = lesson_status.lesson_id
            student = lesson.student
            kwargs['initial'] = kwargs.get('initial', {})

            kwargs['initial']['lesson_name'] = lesson.subject_id.name
            kwargs['initial']['student_name'] = student.user.full_name()
            kwargs['initial']['lesson_date'] = lesson_status.date
            kwargs['initial']['lesson_time'] = lesson_status.time

        super().__init__(*args, **kwargs)

class UpdateLessonRequestForm(forms.ModelForm):
    tutor_name = forms.CharField(label='Tutor', required=False, disabled=True)
    duration = forms.CharField(label='Lesson duration', required=False, disabled=True)

    frequency = forms.CharField(label='Lesson frequency', required=False, disabled=True)

    class Meta:
        model = LessonUpdateRequest
        fields = ['update_option', 'details']

    def __init__(self, *args, **kwargs):
        lesson_update_instance = kwargs.get('instance')
        if lesson_update_instance and lesson_update_instance.lesson:
            kwargs.setdefault('initial', {})
            kwargs['initial']['tutor_name'] = lesson_update_instance.lesson.tutor.user.full_name()
            kwargs['initial']['duration'] = lesson_update_instance.lesson.duration
            kwargs['initial']['frequency'] = lesson_update_instance.lesson.frequency
            kwargs['initial']['subject_name'] = lesson_update_instance.lesson.subject_id.name
        super().__init__(*args, **kwargs)