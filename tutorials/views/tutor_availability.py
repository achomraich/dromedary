from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, get_object_or_404, render
from django.views import View
from django.views.generic import ListView

from tutorials.forms import TutorAvailabilityForm
from tutorials.models import TutorAvailability


"""
This file contains classes to handle 
Tutor availability view
"""

class AvailabilityView(ListView, LoginRequiredMixin):
    """Handles viewing the availability."""
    model = TutorAvailability
    template_name = 'tutor/my_availability/availabilities.html'
    context_object_name = 'availabilities'

    def get_queryset(self):
        """Filter availabilities for the logged-in tutor user."""
        return TutorAvailability.objects.filter(tutor=self.request.user.tutor_profile)

    def post(self, request, *args, **kwargs):
        """Handles POST requests to delete availability."""
        if 'remove' in request.POST:
            availability_id = request.POST.get('availability')
            try:
                availability = TutorAvailability.objects.get(id=availability_id)
                availability.delete()
                messages.success(request, "Deleted successfully.")
            except TutorAvailability.DoesNotExist:
                messages.error(request, "The selected availability does not exist.")
            return redirect('availability')
        else:
            messages.error(request, "Invalid request.")
            return redirect('availability')


class AddEditAvailabilityView(LoginRequiredMixin, View):
    """Handles adding or editing availability."""
    def get(self, request, pk=None, *args, **kwargs):
        """Render a tutor availability form."""
        if pk:
            availability = get_object_or_404(TutorAvailability, pk=pk)
            form = TutorAvailabilityForm(instance=availability)
        else:
            form = TutorAvailabilityForm()

        return render(request, 'tutor/my_availability/add_edit_availability.html', {'form': form, 'pk': pk})

    def post(self, request, pk=None, *args, **kwargs):
        """Handles POST requests to add or edit availability."""
        if pk:
            availability = get_object_or_404(TutorAvailability, pk=pk)
            form = TutorAvailabilityForm(request.POST, instance=availability)
        else:
            form = TutorAvailabilityForm(request.POST)

        if form.is_valid():
            availability = form.save(commit=False)
            # Assign tutor to availability object created
            availability.tutor = request.user.tutor_profile
            availability.save()
            messages.success(request, "Availability saved successfully.")
            return redirect('availability')
        else:
            messages.error(request, "Failed to save availability. Please correct the errors and try again.")

        return render(request, 'tutor/my_availability/add_edit_availability.html', {'form': form, 'pk': pk})