from django import forms
from django.core.exceptions import ValidationError

from tutorials.forms.password import NewPasswordMixin
from tutorials.models import User, Tutor, Student


class SignUpForm(NewPasswordMixin, forms.ModelForm):
    """Form enabling unregistered users to sign up."""

    role = forms.ChoiceField(choices=[('Tutor', 'Tutor'), ('Student', 'Student')])

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