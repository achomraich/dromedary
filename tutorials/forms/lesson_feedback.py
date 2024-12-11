from django import forms

from tutorials.models import LessonStatus


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