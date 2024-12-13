from django import forms

from tutorials.models import LessonStatus


class LessonFeedbackForm(forms.ModelForm):
    """Form to update lesson feedback."""

    """Disabled fields for displaying, not editing."""
    lesson_name = forms.CharField(
        label='Lesson Subject',
        required=True,
        disabled=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    student_name = forms.CharField(
        label='Student',
        required=True,
        disabled=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    lesson_date = forms.DateField(
        label='Lesson Date',
        required=True,
        disabled=True,
        widget=forms.DateInput(attrs={'class': 'form-control'})
    )
    lesson_time = forms.TimeField(
        label='Lesson Time',
        required=True,
        disabled=True,
        widget=forms.TimeInput(attrs={'class': 'form-control'})
    )


    class Meta:
        """Form options."""
        model = LessonStatus
        fields = ['feedback']
        widgets = {
            'feedback': forms.Textarea(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        """Set initial values for certain displayed fields."""
        lesson_status = kwargs.get('instance')
        if lesson_status:
            lesson = lesson_status.lesson_id
            student = lesson.student
            kwargs['initial'] = kwargs.get('initial', {})

            kwargs['initial']['lesson_name'] = lesson.subject.name
            kwargs['initial']['student_name'] = student.user.full_name()
            kwargs['initial']['lesson_date'] = lesson_status.date
            kwargs['initial']['lesson_time'] = lesson_status.time

        super().__init__(*args, **kwargs)