from django import forms

from tutorials.models import Subject


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