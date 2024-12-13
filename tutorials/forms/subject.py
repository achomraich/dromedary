from django import forms

from tutorials.models import Subject


class SubjectForm(forms.ModelForm):
    """Form to create and edit subjects."""
    class Meta:
        """Form options."""
        model = Subject
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        """Set disabled for certain fields."""
        subject = kwargs.get('instance', None)

        super().__init__(*args, **kwargs)

        # Cannot change name if the subject already exists, only description
        if subject and subject.pk:
            self.fields['name'].disabled = True
        else:
            self.fields['name'].disabled = False