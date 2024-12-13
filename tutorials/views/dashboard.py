from django.shortcuts import render
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from tutorials.models import Term


"""
This file contains a view function to handle 
Dashboard
"""

@login_required
def dashboard(request):
    """Display the application's dashboard for each user type."""

    current_user = request.user

    # Get current term
    current_term = Term.objects.filter(
        start_date__lte=timezone.now().date(),
        end_date__gte=timezone.now().date()
    ).first()

    # Current term is to be displayed
    context = {
        'user': current_user,
        'current_term': current_term
    }
    if hasattr(current_user, 'admin_profile'):
        return render(request, 'admin/admin_dashboard.html', context)
    if hasattr(current_user, 'tutor_profile'):
        return render(request, 'tutor/tutor_dashboard.html', context)
    else:
        student = current_user.student_profile
        # If student has notifications about lesson requests, a message shows on the dashboard
        if student.has_new_lesson_notification:
            messages.info(request, 'There has been an update to your lesson requests!')
            student.has_new_lesson_notification = False
            student.save()
        return render(request, 'student/student_dashboard.html', context)