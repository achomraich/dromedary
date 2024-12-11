from django import forms

from tutorials.models import User


class UserForm(forms.ModelForm):
    """Form to update user profiles."""

    class Meta:
        """Form options."""
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'about_me']
        widgets = {
            'about_me': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 5,
                    'placeholder': 'Tell us about yourself (max 2000 characters)'
                }
            )
        }
        error_messages = {
            'username': {
                'unique': "This username already exists. Please use a different one.",
            },
        }