from django import forms

from tutorials.models import LessonUpdateRequest, Tutor, Lesson, Days


class UpdateLessonRequestForm(forms.ModelForm):
    """Form to request an update for lessons."""

    """Disabled fields for displaying, not editing."""
    tutor_name = forms.CharField(
        label='Lesson with',
        required=False,
        disabled=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    duration = forms.CharField(
        label='Lesson duration',
        required=False,
        disabled=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    frequency = forms.CharField(
        label='Lesson frequency',
        required=False,
        disabled=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        """Form options."""
        model = LessonUpdateRequest
        fields = ['update_option', 'details']
        widgets = {
            'update_option': forms.Select(attrs={'class': 'form-select'}),
            'details': forms.Textarea(attrs={'rows': 4, 'cols': 50, 'placeholder': 'Enter additional details here...', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        """Set initial values for certain displayed fields."""
        lesson_update_instance = kwargs.get('instance')
        user = kwargs.pop('user_role', None)
        if lesson_update_instance and lesson_update_instance.lesson:
            kwargs.setdefault('initial', {})
            if user and hasattr(user, 'student_profile'):
                kwargs['initial']['tutor_name'] = lesson_update_instance.lesson.tutor.user.full_name()
            if user and hasattr(user, 'tutor_profile'):
                kwargs['initial']['tutor_name'] = lesson_update_instance.lesson.student.user.full_name()
            kwargs['initial']['duration'] = lesson_update_instance.lesson.duration
            kwargs['initial']['frequency'] = lesson_update_instance.lesson.get_frequency_display()
            kwargs['initial']['subject_name'] = lesson_update_instance.lesson.subject.name

        # Populate update option choices if the attribute of the object has values 1 or 2
        # 1: Change Tutor 2: Change Day/Time
        super().__init__(*args, **kwargs)
        if user:
            if hasattr(user, 'tutor_profile'):
                self.fields['update_option'].choices = [
                    choice for choice in LessonUpdateRequest.UpdateOption.choices if choice[0] == '2' or choice[0] == '1'
                ]

class UpdateLessonForm(forms.ModelForm):
    """Form to handle requests for lesson updating."""

    """Disabled fields for displaying and field attribute setting."""
    frequency = forms.CharField(label='Lesson frequency', required=False, disabled=True)
    details = forms.CharField(
        label='Request details',
        disabled=True
    )
    subject = forms.CharField(label='Subject', required=True, disabled=True)
    duration = forms.TimeField(label='Lesson Duration', required=False, disabled=True)
    day_of_week = forms.CharField(label='Current lesson\'s day of week', required=False, disabled=True)
    lesson_time = forms.TimeField(label='Current lesson\'s time', required=False,  disabled=True)

    new_day_of_week = forms.DateField(label='Choose date for the next lesson', required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    new_tutor = forms.ModelChoiceField(
        queryset=Tutor.objects.all(),

        label='New Tutor',
        required=False
    )
    new_lesson_time = forms.TimeField(label='New lesson time', required=True,
        widget=forms.TimeInput(attrs={'type': 'time'}))
    next_lesson=forms.DateField(label='Next lesson planned on', required=False, disabled=True)

    class Meta:
        """Form options."""
        model = Lesson
        fields = ['tutor', 'student', 'new_tutor', 'new_day_of_week', 'new_lesson_time']


    def __init__(self, *args, **kwargs):
        """Set initial values and query sets for certain fields."""

        lesson_update_instance = kwargs.get('instance', None)
        option = kwargs.pop('update_option', None)
        day_of_week = kwargs.pop('day_of_week', None)
        details = kwargs.pop('details', None)
        lesson_time = kwargs.pop('regular_lesson_time', None)
        next_lesson_date = kwargs.pop('next_lesson_date', None)

        kwargs.setdefault('initial', {})

        # If there is an instance, populate the form with existing values
        if lesson_update_instance:

            day_of_week_display = dict(Days.choices).get(day_of_week, "Unknown Day")

            kwargs['initial'].update({
                'details': details,
                'duration': str(lesson_update_instance.duration),
                'frequency': lesson_update_instance.get_frequency_display(),
                'lesson_time': lesson_time,
                'subject': lesson_update_instance.subject.name,
                'day_of_week': day_of_week_display,
                'new_lesson_time': None,
                'next_lesson': next_lesson_date
            })

        # Set certain fields to disable.
        super().__init__(*args, **kwargs)
        if lesson_update_instance:
            self.fields['tutor'].disabled = True
            self.fields['student'].disabled = True
            self.fields['subject'].disabled = True
            self.fields['duration'].disabled = True
        if lesson_update_instance.subject:
            subject_name = lesson_update_instance.subject
            self.fields['new_tutor'].queryset = Tutor.objects.filter(subjects__name=subject_name)
