from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View

from tutorials.forms import AssignTutorForm, LessonRequestForm
from tutorials.models import LessonRequest, Lesson, Status


"""
This file contains classes to handle 
Requests 
"""

class RequestView(LoginRequiredMixin, View):
    """ Handles request list views for admin and users"""
    status = None
    requests_list = None

    def get(self, request, request_id=None):
        current_user = request.user

        if request_id:
            return self.request_assign(request, request_id)

        if hasattr(current_user, 'admin_profile'):
            self.requests_list = LessonRequest.objects.all().order_by('-created')
            self.status = 'admin'
        elif hasattr(request.user, 'student_profile'):
            self.requests_list = LessonRequest.objects.filter(student=current_user.id).order_by('-created')
            self.status = 'student'
        else:
            messages.error(request, "Tutors may not request lessons.")
            return redirect('dashboard')
        return render(request, f'{self.status}/requests/requests.html', {"lesson_requests": self.requests_list})

    def post(self, request, *args, **kwargs):
        lrequest_id = request.POST.get('request_id')
        if not lrequest_id:
            messages.error(request, "No entity ID provided for the operation.")
            return redirect('requests')

        lrequest = get_object_or_404(LessonRequest, id=lrequest_id)

        if 'edit' in request.POST:
            return self.assign_tutor(request, lrequest)
        elif 'reject' in request.POST:
            return self.reject_request(request, lrequest)
        elif 'cancel' in request.POST:
            return self.cancel_request(request, lrequest)

        messages.error(request, "Invalid operation.")
        return redirect('requests')

    def request_assign(self, request, request_id, form=None):
        lrequest = get_object_or_404(LessonRequest, id=request_id)
        lrequest.refresh_from_db()

        if not form:
            form = AssignTutorForm(existing_request=lrequest)

        return render(request, 'admin/requests/assign_tutor.html', {'form' : form, 'request': lrequest})

    def assign_tutor(self, request, lrequest):
        ''' Allows admin to assign a tutor to the request by student'''
        form = AssignTutorForm(request.POST, existing_request=lrequest)
        if form.is_valid():
            self.create_lesson(request, lrequest, form)
            messages.success(request, "Request assigned successfully.")
            return redirect('requests')
        else:
            messages.error(request, "Failed to update details. Please correct the errors and try again.")
            lrequest.refresh_from_db()
            return self.request_assign(request, lrequest.id, form)

    def create_lesson(self, request, lrequest, form):
        tutor = form.cleaned_data['tutor']
        price_per_lesson = form.cleaned_data['price_per_lesson']

        # Create a new Lesson based on the form data and LessonRequest details
        lesson = Lesson.objects.create(
            tutor=tutor,
            student=lrequest.student,
            subject=lrequest.subject,
            term=lrequest.term,
            frequency="W",  # Assuming "W" for weekly frequency, can be updated if needed
            duration=lrequest.duration,  # Duration from the LessonRequest
            set_start_time=lrequest.time,
            start_date=lrequest.start_date,
            price_per_lesson=price_per_lesson,
        )
        lrequest.lesson_assigned = lesson
        lrequest.status = Status.CONFIRMED
        lrequest.save()
        self.toggle_notification(request, lrequest)


    def reject_request(self, request, lrequest):
        ''' Allows admin to reject a request '''
        lrequest.status = Status.REJECTED
        lrequest.save()
        self.toggle_notification(request, lrequest)

        messages.success(request, "Request rejected.")
        return redirect('requests')

    def toggle_notification(self, request, lrequest):
        ''' Handles notification to inform a student the there is updates on their request '''
        lrequest.student.has_new_lesson_notification = True
        lrequest.student.save()

    def cancel_request(self, request, lrequest):
        lrequest.status = Status.CANCELLED
        lrequest.save()
        messages.success(request, "Request cancelled.")
        return redirect('requests')


class MakeRequestView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        form = LessonRequestForm()
        return render(request, 'student/requests/lesson_request_form.html', {'form': form})


    def post(self, request, *args, **kwargs):
        form = LessonRequestForm(request.POST)
        if form.is_valid():
            # Create lesson request but don't save it yet
            lesson_request = form.save(commit=False)
            # Associate the logged-in student's profile with the lesson request
            lesson_request.student = request.user.student_profile
            # Save the lesson request to the database
            lesson_request.save()
            messages.success(request, "Request submitted successfully.")
            # Redirect to a success page or another page after form submission
            return redirect('requests')
        else:
            messages.error(request, "Failed to update details. Please correct the errors and try again.")

        return render(request, 'student/requests/lesson_request_form.html', {'form': form})
