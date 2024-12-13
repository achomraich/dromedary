from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import FormView, TemplateView

from tutorials.forms import PasswordForm, TutorForm, UserForm


"""
This file contains view classes to handle and update 
Password
"""

class PasswordView(LoginRequiredMixin, FormView):
    """Display password change screen and handle password change requests."""

    template_name = 'password.html'
    form_class = PasswordForm

    def get_form_kwargs(self, **kwargs):
        """Pass the current user to the password change form."""

        kwargs = super().get_form_kwargs(**kwargs)
        kwargs.update({'user': self.request.user})
        return kwargs

    def form_valid(self, form):
        """Handle valid form by saving the new password."""

        form.save()
        login(self.request, self.request.user)
        return super().form_valid(form)

    def get_success_url(self):
        """Redirect the user after successful password change."""

        messages.add_message(self.request, messages.SUCCESS, "Password updated!")
        return reverse('dashboard')


class ProfileUpdateView(LoginRequiredMixin, TemplateView):
    template_name = "profile.html"

    def get_context_data(self, **kwargs):
        """Add forms to the context."""
        context = super().get_context_data(**kwargs)

        # Add tutor form with extra fields "experience" and "subjects"
        if hasattr(self.request.user, 'tutor_profile'):
            tutor_form = TutorForm(instance=self.request.user.tutor_profile)
        else:
            tutor_form = None

        context['user_form'] = UserForm(instance=self.request.user)
        context['tutor_form'] = tutor_form
        return context

    def post(self, request, *args, **kwargs):
        """Handles form submission."""
        user_form = UserForm(self.request.POST, instance=self.request.user)
        if hasattr(self.request.user, 'tutor_profile'):
            tutor_form = TutorForm(self.request.POST, instance=self.request.user.tutor_profile)
        else:
            tutor_form = None  # Don't handle tutor form if no tutor profile

        self.save_forms(user_form, tutor_form)

        if self.forms_are_valid(user_form, tutor_form):
            messages.success(request, "Profile updated successfully!")
            return redirect(self.get_success_url())

        return self.render_to_response(self.get_context_data(form={'user_form': user_form, 'tutor_form': tutor_form}))

    @staticmethod
    def get_success_url():
        """Redirect after successful update."""
        return reverse(settings.REDIRECT_URL_WHEN_LOGGED_IN)

    @staticmethod
    def save_forms(user_form, tutor_form):
        if user_form.is_valid():
            user_form.save()
        if tutor_form and tutor_form.is_valid():
            tutor_form.save()

    @staticmethod
    def forms_are_valid(user_form, tutor_form):
        if user_form.is_valid() and (tutor_form is None or tutor_form.is_valid()):
            return True
