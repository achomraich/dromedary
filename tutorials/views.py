from functools import reduce

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.db import IntegrityError
from django.db.models import Q
from django.shortcuts import redirect, render, get_object_or_404
from django.http import Http404, HttpResponseForbidden, HttpResponseRedirect
from django.views import View
from django.views.generic.edit import FormView, UpdateView
from django.urls import reverse
from tutorials.forms import LogInForm, PasswordForm, UserForm, SignUpForm
from tutorials.helpers import login_prohibited
from django.core.paginator import Paginator
from .models import Invoice
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from tutorials.models import Student, Admin, Tutor, Subject
from tutorials.models import Lesson, LessonStatus, Tutor
import logging

@login_required
def dashboard(request):
    current_user = request.user
    if hasattr(current_user, 'admin_profile'):
        return render(request, 'admin/admin_dashboard.html', {'user': current_user})
    if hasattr(current_user, 'tutor_profile'):
        return render(request, 'tutor/tutor_dashboard.html', {'user': current_user})
    else:
        return render(request, 'student/student_dashboard.html', {'user': current_user})

@login_required
def lesson_requests(request):
    """Display the lesson requests to the current user."""

    current_user = request.user
    return render(request, 'requests.html', {'user': current_user})


@login_prohibited
def home(request):
    """Display the application's start/home screen."""

    return render(request, 'home.html')


class LoginProhibitedMixin:
    """Mixin that redirects when a user is logged in."""

    redirect_when_logged_in_url = None

    def dispatch(self, *args, **kwargs):
        """Redirect when logged in, or dispatch as normal otherwise."""
        if self.request.user.is_authenticated:
            return self.handle_already_logged_in(*args, **kwargs)
        return super().dispatch(*args, **kwargs)

    def handle_already_logged_in(self, *args, **kwargs):
        url = self.get_redirect_when_logged_in_url()
        return redirect(url)

    def get_redirect_when_logged_in_url(self):
        """Returns the url to redirect to when not logged in."""
        if self.redirect_when_logged_in_url is None:
            raise ImproperlyConfigured(
                "LoginProhibitedMixin requires either a value for "
                "'redirect_when_logged_in_url', or an implementation for "
                "'get_redirect_when_logged_in_url()'."
            )
        else:
            return self.redirect_when_logged_in_url


class LogInView(LoginProhibitedMixin, View):
    """Display login screen and handle user login."""

    http_method_names = ['get', 'post']
    redirect_when_logged_in_url = settings.REDIRECT_URL_WHEN_LOGGED_IN

    def get(self, request):
        """Display log in template."""

        self.next = request.GET.get('next') or ''
        return self.render()

    def post(self, request):
        """Handle log in attempt."""

        form = LogInForm(request.POST)
        self.next = request.POST.get('next') or settings.REDIRECT_URL_WHEN_LOGGED_IN
        user = form.get_user()
        if user is not None:
            login(request, user)
            return redirect(self.next)
        messages.add_message(request, messages.ERROR, "The credentials provided were invalid!")
        return self.render()

    def render(self):
        """Render log in template with blank log in form."""

        form = LogInForm()
        return render(self.request, 'log_in.html', {'form': form, 'next': self.next})


def log_out(request):
    """Log out the current user"""

    logout(request)
    return redirect('home')


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


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Display user profile editing screen, and handle profile modifications."""

    model = UserForm
    template_name = "profile.html"
    form_class = UserForm

    def get_object(self):
        """Return the object (user) to be updated."""
        user = self.request.user
        return user

    def get_success_url(self):
        """Return redirect URL after successful update."""
        messages.add_message(self.request, messages.SUCCESS, "Profile updated!")
        return reverse(settings.REDIRECT_URL_WHEN_LOGGED_IN)


class SignUpView(LoginProhibitedMixin, FormView):
    """Display the sign up screen and handle sign ups."""

    form_class = SignUpForm
    template_name = "sign_up.html"
    redirect_when_logged_in_url = settings.REDIRECT_URL_WHEN_LOGGED_IN

    def form_valid(self, form):
        self.object = form.save()
        login(self.request, self.object)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(settings.REDIRECT_URL_WHEN_LOGGED_IN)

def invoice_management(request):
        if request.method == 'POST':
            # Process the form to create a new invoice
            student_name = request.POST.get('student')
            amount = request.POST.get('amount')
            due_date = request.POST.get('due_date')
            is_paid = request.POST.get('is_paid') == 'on'

            # Create a new Invoice
            Invoice.objects.create(
                student=student_name,
                amount=amount,
                due_date=due_date,
                is_paid=is_paid
            )
            return redirect('invoice_management')  # Redirect to avoid form resubmission

        # Fetch existing invoices to display
        invoices = Invoice.objects.all()
        return render(request, 'invoices/invoice_management.html', {'invoices': invoices})

@require_POST
def create_invoice(request):
    # Extract form data
    student_username = request.POST.get('student')
    amount = request.POST.get('amount')
    due_date = request.POST.get('due_date')
    is_paid = request.POST.get('is_paid') == 'on'

    # Get the User instance based on the provided student username
    student = get_object_or_404(User, username=student_username)

    # Create a new Invoice record
    Invoice.objects.create(
        student=student,  # Use the User instance here
        amount=amount,
        due_date=due_date,
        is_paid=is_paid
    )

    # Redirect back to the invoice management page
    return redirect('invoice_management')

class EntityView(View):
    model = None
    list_admin = None
    list_user = None
    details = None
    edit = None
    redirect_url = None

    def get(self, request, *args, **kwargs):
        entity_id = kwargs.get('tutor_id') or kwargs.get('student_id')
        if entity_id:
            return self.entity_details(request, entity_id)
        else:
            return self.get_entities(request)
        
    def post(self, request, *args, **kwargs):
        entity_id = request.POST.get('entity_id')
        if not entity_id:
            messages.error(request, "No entity ID provided for the operation.")
            return redirect(self.redirect_url)

        entity = get_object_or_404(self.model, user__id=entity_id)

        if 'edit' in request.POST:
            return self.edit_entity(request, entity)
        elif 'delete' in request.POST:
            return self.delete_entity(request, entity)

        messages.error(request, "Invalid operation.")
        return redirect(self.redirect_url)

    def get_entities(self, request):
        user = request.user
        search = request.GET.get('search', '')
        subjects = Subject.objects.all()

        profile_map = {
            'admin_profile': lambda: self.model.objects.all().order_by('user__username'),
            'tutor_profile': lambda: self._get_entities_for_tutor(user),
            'student_profile': lambda: self._get_entities_for_student(user),
        }

        entity_list = None
        for profile, entity_filter in profile_map.items():
            if hasattr(user, profile):
                entity_list = entity_filter()
                break

        if not entity_list:
            #messages.error(request, "No valid profile for this operation.")
            print('got there')
            raise PermissionDenied("No valid profile for this operation.")

        if search:
            query = reduce(lambda q1, q2: q1 | q2, [
                Q(user__username__icontains=search),
                Q(user__first_name__icontains=search),
                Q(user__last_name__icontains=search),
                Q(user__email__icontains=search)
            ])
            entity_list = entity_list.filter(query)

        entity_list = self.apply_filters(request, entity_list)
        page_number = request.GET.get('page', 1)
        paginator = Paginator(entity_list, 20)
        page_obj = paginator.get_page(page_number)

        template = self.list_admin if hasattr(request.user, 'admin_profile') else self.list_user
        return render(request, template, {
            'page_obj': page_obj,
            'user': user,
            'search_query': search,
            'subject_query': request.GET.get('subject', ''),
            'subjects': subjects
        })

    def _get_entities_for_tutor(self, user):
        lessons = Lesson.objects.filter(tutor_id=user.id)
        return self.model.objects.filter(user_id__in=lessons.values('student_id')).order_by('user__username').distinct()

    def _get_entities_for_student(self, user):
        lessons = Lesson.objects.filter(student_id=user.id)
        return self.model.objects.filter(user_id__in=lessons.values('tutor_id')).order_by('user__username').distinct()

    def entity_details(self, request, entity_id):
        entity = get_object_or_404(self.model, user__id=entity_id)

        lessons = None
        tutors = None
        students = None

        if isinstance(entity, Student):
            lessons = Lesson.objects.filter(student=entity).select_related(
            'tutor', 'subject_id', 'term_id'
        )
        
            tutors = set(lesson.tutor for lesson in lessons)

        else:
            lessons = Lesson.objects.filter(tutor=entity)
        
            students = set(lesson.student for lesson in lessons)

        content = {
            self.model.__name__.lower(): entity,  
            'lessons': lessons, 
            'tutors': tutors,  
            'students': students,
        }
        if request.path.endswith('edit/'):
            print("i'm here")
            return self.edit_form(request, entity)
        else:
            return render(request, self.details, content)
        
    def edit_form(self, request, entity, form=None):
        entity.refresh_from_db()
        if not form:
            form = UserForm(instance = entity.user)
        return render(request, self.edit, {'form' : form, self.model.__name__.lower(): entity})
    
    def edit_entity(self, request, entity):
        form = UserForm(request.POST, instance=entity.user)

        if form.is_valid():
            form.save()
            messages.success(request, "Details updated successfully.")
            return redirect(self.redirect_url)
        else:
            print("Form errors:", form.errors.as_data())
            messages.error(request, "Failed to update details. Please correct the errors and try again.")

        return self.edit_form(request, entity, form)
    
    def delete_entity(self, request, entity):
        entity.user.delete()
        messages.success(request, "Deleted successfully.")
        return redirect(self.redirect_url)
    
    
    
class StudentsView(EntityView):
    model = Student

    list_admin = 'admin/manage_students/students_list.html'
    list_user = 'tutor/my_students/students_list.html'
    details = 'admin/manage_students/student_details.html'
    edit = 'admin/manage_students/edit_student.html'
    redirect_url = 'students_list'

    def get(self, request, student_id=None, *args, **kwargs):
        
        return super().get(request, student_id=student_id, *args, **kwargs)
    
    def post(self, request, student_id=None, *args, **kwargs):
        return super().post(request, student_id=student_id, *args, **kwargs)

    def apply_filters(self, request, entity_list):
        subject_filter = request.GET.get('subject', '')
        if subject_filter:
            filtered_lessons = Lesson.objects.filter(subject_id__name=subject_filter)
            entity_list = entity_list.filter(user_id__in=filtered_lessons.values('student_id')).distinct() 
        return entity_list

class TutorsView(EntityView):
    model = Tutor

    list_admin = 'admin/manage_tutors/tutors_list.html'
    list_user = 'student/my_tutors/tutors_list.html'
    details = 'admin/manage_tutors/tutor_details.html'
    edit = 'admin/manage_tutors/edit_tutor.html'
    redirect_url = 'tutors_list'

    def get(self, request, tutor_id=None, *args, **kwargs):
        return super().get(request, tutor_id=tutor_id, *args, **kwargs)
    
    def post(self, request, tutor_id=None, *args, **kwargs):
        return super().post(request, tutor_id=tutor_id, *args, **kwargs)
    
    def apply_filters(self, request, entity_list):
        subject_filter = request.GET.get('subject', '')
        if subject_filter:
            filtered_lessons = Lesson.objects.filter(subject_id__name=subject_filter)
            entity_list = entity_list.filter(user_id__in=filtered_lessons.values('tutor_id')).distinct()
        return entity_list


class ViewLessons(View):

    def get(self, request, lesson_id=None):
        current_user = request.user
        if lesson_id:
            return self.lesson_detail(request, lesson_id)

        if hasattr(current_user, 'admin_profile'):
            self.list_of_lessons = Lesson.objects.all()
        elif hasattr(request.user, 'student_profile'):
            self.list_of_lessons = Lesson.objects.filter(student=current_user.id)
        else:
            self.list_of_lessons = Lesson.objects.filter(tutor=current_user.id)
        return render(request, 'shared/lessons/lessons_list.html', {"list_of_lessons": self.list_of_lessons})


    def lesson_detail(self, request, lesson_id):
        """Display each lesson status for admin"""
        try:
            lessonStatus = LessonStatus.objects.filter(lesson_id=lesson_id)
        except Exception as e:
            raise Http404(f"Could not find lesson with primary key {lesson_id}")
        else:
            context = {"lessons": lessonStatus}
            return render(request, 'shared/lessons/lessons_details.html', context)

