from django import forms

from tutorials.models import Subject, Tutor


class TutorForm(forms.ModelForm):
    subjects = forms.ModelMultipleChoiceField(
        queryset=Subject.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-inline'}),
        required=False,
        label="Subjects Taught"
    )

    class Meta:
        model = Tutor
        fields = ['experience', 'subjects']
        widgets = {
            'experience': forms.Textarea(attrs={'rows': 3,'placeholder': 'Tell us more about your experience in teaching...'}),
        }
        labels = {
            'experience': 'Experience',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        tutor = kwargs.get('instance', None)
        if tutor and hasattr(tutor, 'user') and tutor.user:
            self.fields['subjects'].queryset = Subject.objects.all()