from django import forms

from tutorials.models import TutorAvailability


class TutorAvailabilityForm(forms.ModelForm):
    """Form to add or edit tutor's availability."""
    class Meta:
        """Form options."""
        model = TutorAvailability
        fields = ['day', 'start_time', 'end_time', 'status']
        widgets = {
            'start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'end_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'day': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        """Set day and status fields to display 'Select an option' as the default selection"""

        super().__init__(*args, **kwargs)
        self.fields['day'].choices = [('', 'Select an option')] + [
            choice for choice in self.fields['day'].choices if choice[0] != ''
        ] # Adds 'Select an option' as a choice in the list of choices in form
        self.fields['status'].choices = [('', 'Select an option')] + [
            choice for choice in self.fields['status'].choices if choice[0] != ''
        ]



class TutorAvailabilityList(forms.Form):
    """Form to select tutors for viewing availabilities in lesson update requests."""

    # Radio buttons for selecting "Current Tutor" or "Other Tutors"
    tutor_selection = forms.ChoiceField(
        label="Select Tutor Option",
        choices=[
            ('current', 'Current Tutor'),
            ('other', 'Other Tutors')
        ],
        widget=forms.RadioSelect,
        initial='current'  # Default to "Current Tutor"
    )

    # Hidden field to dynamically populate tutor availability data
    availability_table = forms.CharField(
        label="",
        required=False,
        widget=forms.HiddenInput
    )

    def __init__(self, *args, **kwargs):
        """Set attributes for the current tutor name field."""
        current_tutor = kwargs.pop('current_tutor', None)  # Pass the current tutor
        super().__init__(*args, **kwargs)

        if current_tutor:
            # Add the current tutor name for display
            self.fields['current_tutor_name'] = forms.CharField(
                label="Current Tutor",
                initial=current_tutor.user.full_name(),
                disabled=True,
                required=False,
                widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'})
            )
