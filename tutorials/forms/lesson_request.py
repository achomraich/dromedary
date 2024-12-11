from django import forms

from tutorials.models import LessonRequest, Lesson


class LessonRequestForm(forms.ModelForm):
    class Meta:
        model = LessonRequest
        fields = ['subject','term','start_date','time','duration','frequency']
        widgets = {
            'time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'frequency': forms.Select(attrs={'class': 'form-select'}),
            'term': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['subject'].empty_label = "Select a subject"
        self.fields['frequency'].choices = [('', 'Select a frequency')] + [
            choice for choice in self.fields['frequency'].choices if choice[0] != ''
        ]
        self.fields['term'].empty_label = "Select an academic term"


class AssignTutorForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['student', 'tutor', 'subject','term','duration','frequency', 'start_date', 'price_per_lesson']
        widgets = {
            'tutor': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control'}),
            'price_per_lesson': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter price'}),
        }

    def __init__(self, *args, existing_request=None, **kwargs):
        super().__init__(*args, **kwargs)
        if existing_request:
            self.fields['student'].initial = existing_request.student
            self.fields['student'].disabled = True
            self.fields['subject'].initial = existing_request.subject
            self.fields['subject'].disabled = True
            self.fields['term'].initial = existing_request.term
            self.fields['term'].disabled = True
            self.fields['duration'].initial = existing_request.duration
            self.fields['duration'].disabled = True
            self.fields['frequency'].initial = existing_request.frequency
            self.fields['frequency'].disabled = True
            self.fields['start_date'].initial = existing_request.start_date
            self.fields['start_date'].disabled = True
        self.fields['tutor'].empty_label = "Select a tutor"
        self.fields['price_per_lesson'].label = "Select a price per lesson ($)"
