"""Forms for the tutorials app."""
from django import forms
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from .models import User, Tutor, Student, Subject, LessonStatus, LessonUpdateRequest, Lesson

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

    role = forms.ChoiceField(choices=[('Tutor', 'Tutor'), ('Student', 'Student'), ('Admin', 'Admin')])

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
    lesson_name = forms.CharField(label='Lesson Subject', required=True, disabled=True)
    student_name = forms.CharField(label='Student', required=True, disabled=True)
    lesson_date = forms.DateField(label='Lesson Date', required=True, disabled=True)
    lesson_time = forms.TimeField(label='Lesson Time', required=True, disabled=True)

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
    tutor_name = forms.CharField(label='Lesson with: ', required=False, disabled=True)
    duration = forms.CharField(label='Lesson duration: ', required=False, disabled=True)
    frequency = forms.CharField(label='Lesson frequency: ', required=False, disabled=True)

    class Meta:
        model = LessonUpdateRequest
        fields = ['update_option', 'details']
        widgets = {
            'details': forms.Textarea(attrs={'rows': 4, 'cols': 50, 'placeholder': 'Enter additional details here...'}),
        }

    def __init__(self, *args, **kwargs):
        lesson_update_instance = kwargs.get('instance')
        user = kwargs.pop('user_role', None)
        if lesson_update_instance and lesson_update_instance.lesson:
            kwargs.setdefault('initial', {})
            if user and hasattr(user, 'student_profile'):
                kwargs['initial']['tutor_name'] = lesson_update_instance.lesson.tutor.user.full_name()
            if user and hasattr(user, 'tutor_profile'):
                kwargs['initial']['tutor_name'] = lesson_update_instance.lesson.student.user.full_name()
            kwargs['initial']['duration'] = lesson_update_instance.lesson.duration
            kwargs['initial']['frequency'] = lesson_update_instance.lesson.frequency
            kwargs['initial']['subject_name'] = lesson_update_instance.lesson.subject_id.name

        super().__init__(*args, **kwargs)
        if user:
            if hasattr(user, 'tutor_profile'):
                self.fields['update_option'].choices = [
                    choice for choice in LessonUpdateRequest.UPDATE_CHOICES if choice[0] == '2' or choice[0] == '3'
                ]
'''
class UpdateLessonForm(forms.ModelForm):
    tutor_name = forms.CharField(label='Tutor', required=False)
    student = forms.CharField(label='Student', required=False, disabled=True)
    frequency = forms.CharField(label='Lesson frequency', required=False)
    update_option = forms.CharField(label='Request', required=False, disabled=True)
    details = forms.CharField(label='Request details', required=False, disabled=True)
    duration = forms.TimeField(label='Lesson Duration', required=False)
    day_of_week = forms.DateField(label='Day of Week', required=False)

    class Meta:
        model = Lesson
        fields = ['tutor_name', 'frequency', 'duration', 'day_of_week']

    def __init__(self, *args, **kwargs):
        # Extract arguments
        lesson_update_instance = kwargs.get('instance', None)
        option = kwargs.pop('update_option', None)
        day_of_week = kwargs.pop('day_of_week', None)
        details = kwargs.pop('details', None)

        # Initialize initial data after form creation
        super().__init__(*args, **kwargs)

        if lesson_update_instance:
            # Manually set the initial data
            self.fields['student'].initial = lesson_update_instance.student.user.full_name() if lesson_update_instance.student else ''
            self.fields['tutor_name'].initial = lesson_update_instance.tutor.user.full_name() if lesson_update_instance.tutor else ''
            print(lesson_update_instance.tutor.user.full_name())
            self.fields['update_option'].initial = option
            self.fields['details'].initial = details
            self.fields['duration'].initial = lesson_update_instance.duration
            self.fields['day_of_week'].initial = day_of_week
            self.fields['frequency'].initial = lesson_update_instance.frequency

            # Debugging: Check if initial values are set correctly
            print("Field values after initialization:")
            print(f"tutor_name: {self.fields['tutor_name'].initial}")
            print(f"frequency: {self.fields['frequency'].initial}")
            print(f"duration: {self.fields['duration'].initial}")
            print(f"day_of_week: {self.fields['day_of_week'].initial}")

        # Set the fields' properties: Make sure fields are editable if required
        self.fields['tutor_name'].disabled = False
        self.fields['frequency'].disabled = False
        self.fields['duration'].disabled = False
        self.fields['day_of_week'].disabled = False
'''
'''
class UpdateLessonForm(forms.ModelForm):
    tutor_name = forms.CharField(label='Tutor', required=False, disabled=True)
    student = forms.CharField(label='Student', required=False, disabled=True)
    frequency = forms.CharField(label='Lesson frequency', required=False, disabled=True)
    update_option = forms.CharField(label='Request', required=False, disabled=True)
    details = forms.CharField(
        label='Request details',
        required=False,
        widget=forms.Textarea(attrs={'rows': 4, 'cols': 50, 'placeholder': 'Enter additional details here...'}),
        disabled=True
    )
    duration = forms.TimeField(label='Lesson Duration', required=False, disabled=True)
    day_of_week = forms.CharField(label='Choose date for the next lesson', required=False)
    lesson_time = forms.CharField(label='Time', required=False)
    new_frequency = forms.CharField(label='New Frequency', required=True)

    new_tutor = forms.CharField(label='Subject ', required=True)

    class Meta:
        model = Lesson
        fields = ['new_tutor', 'update_option', 'details', 'new_frequency', 'day_of_week', 'lesson_time']

    def __init__(self, *args, **kwargs):
        # Extract the extra parameters passed to the form
        lesson_update_instance = kwargs.get('instance', None)
        option = kwargs.pop('update_option', None)
        day_of_week = kwargs.pop('day_of_week', None)
        details = kwargs.pop('details', None)
        lesson_time = kwargs.pop('regular_lesson_time', None)
        new_tutor = kwargs.pop('new_tutor', None)

        kwargs.setdefault('initial', {})

        if lesson_update_instance:
            kwargs['initial'].update({
                'student': lesson_update_instance.student.user.full_name() if lesson_update_instance.student else '',
                'tutor_name': lesson_update_instance.tutor.user.full_name() if lesson_update_instance.tutor else '',
                'update_option': option,
                'details': details,
                'duration': str(lesson_update_instance.duration),
                'frequency': lesson_update_instance.frequency,
                'lesson_time': lesson_time,
                'day_of_week': day_of_week,
                'subject': lesson_update_instance.subject_id.name,
                'new_tutor': new_tutor if new_tutor else '',
            })

        super().__init__(*args, **kwargs)

        self.fields['subject'].disabled = True
        self.fields['student'].disabled = True

        if option == 'Change Tutor':

            self.fields['lesson_time'].disabled = True
            self.fields['duration'].disabled = True
            self.fields['tutor_name'].disabled = True
            self.fields['day_of_week'].disabled = True

            self.fields['new_tutor'].disabled = False

        elif option == 'Change Day/Time':

            self.fields['duration'].disabled = True
            self.fields['tutor_name'].disabled = True

            #self.fields['day_of_week'].disabled = False
            self.fields['lesson_time'].disabled = False
            self.fields['lesson_time'].disabled = False
            #self.fields['new_tutor'].disabled = True  # has to be changed if tutor is unavailable

        elif option == 'Cancel Lessons':

            self.fields['lesson_time'].disabled = True
            self.fields['duration'].disabled = True
            self.fields['tutor_name'].disabled = True
            self.fields['day_of_week'].disabled = True

        elif option == 'Change Frequency':
            self.fields['day_of_week'].disabled = True
            self.fields['lesson_time'].disabled = True
        elif option == 'Change Duration of the Lesson':

            self.fields['day_of_week'].disabled = True
            self.fields['lesson_time'].disabled = True
'''

class UpdateLessonForm(forms.ModelForm):
    tutor_name = forms.CharField(label='Tutor', required=False, disabled=True)
    student = forms.CharField(label='Student', required=False, disabled=True)
    frequency = forms.CharField(label='Lesson frequency', required=False, disabled=True)
    update_option = forms.CharField(label='Request', required=False, disabled=True)
    details = forms.CharField(
        label='Request details',
        disabled=True
    )
    subject = forms.CharField(label='Subject', required=True, disabled=True)
    duration = forms.TimeField(label='Lesson Duration', required=False, disabled=True)
    day_of_week = forms.CharField(label='Current lesson\'s day of week', required=False, disabled=True)
    lesson_time = forms.TimeField(label='Current lesson\'s time', required=False,  disabled=True)

    new_day_of_week = forms.DateField(label='Choose date for the next lesson', required=False,widget=forms.DateInput(attrs={'type': 'date'}))
    new_frequency = forms.CharField(label='New Frequency', required=False)
    new_tutor = forms.CharField(label='New Tutor', required=False)
    new_lesson_time = forms.TimeField(label='New lesson time', required=True,
        widget=forms.TimeInput(attrs={'type': 'time'}))

    class Meta:
        model = Lesson
        fields = ['new_tutor', 'new_frequency', 'new_day_of_week', 'new_lesson_time']

    def __init__(self, *args, **kwargs):
        # Extract extra parameters passed to the form
        lesson_update_instance = kwargs.get('instance', None)
        option = kwargs.pop('update_option', None)
        day_of_week = kwargs.pop('day_of_week', None)
        details = kwargs.pop('details', None)
        lesson_time = kwargs.pop('regular_lesson_time', None)

        kwargs.setdefault('initial', {})

        if lesson_update_instance:
            kwargs['initial'].update({
                'student': lesson_update_instance.student.user.full_name() if lesson_update_instance.student else '',
                'tutor_name': lesson_update_instance.tutor.user.full_name() if lesson_update_instance.tutor else '',
                'update_option': option,
                'details': details,
                'duration': str(lesson_update_instance.duration),
                'frequency': lesson_update_instance.frequency,
                'lesson_time': lesson_time,
                'subject': lesson_update_instance.subject_id.name,
                'day_of_week': day_of_week,
                'new_lesson_time': None
            })

        super().__init__(*args, **kwargs)

        # Fields common to all options
        common_fields = ['student', 'tutor_name', 'update_option', 'details', 'subject']

        # Define fields for each option
        fields_for_option = {
            'Change Tutor': common_fields + ['new_tutor'],
            'Change Day/Time': common_fields + ['new_day_of_week', 'new_lesson_time', 'day_of_week', 'lesson_time'],
            'Cancel Lessons': common_fields + ['day_of_week', 'lesson_time', 'duration'],
            'Change Frequency': common_fields + ['new_frequency'],
            'Change Duration of the Lesson': common_fields + ['duration']
        }

        # Set default to hide all fields
        all_fields = set(self.fields.keys())
        displayed_fields = set(fields_for_option.get(option, common_fields))
        hidden_fields = all_fields - displayed_fields

        # Disable or hide fields as needed
        for field_name in hidden_fields:
            self.fields[field_name].disabled = True
            self.fields[field_name].widget = forms.HiddenInput()

