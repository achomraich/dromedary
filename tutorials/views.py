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
from django.views.generic import TemplateView
from django.views.generic.edit import FormView, UpdateView
from django.urls import reverse
from tutorials.forms import LogInForm, PasswordForm, UserForm, SignUpForm, SubjectForm, LessonFeedbackForm, UpdateLessonRequestForm, LessonRequestForm, TutorForm
from tutorials.helpers import login_prohibited
from django.core.paginator import Paginator
from django.utils.timezone import now
from datetime import timedelta, datetime
import calendar
from .models import Invoice
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from tutorials.models import Student, Admin, Tutor, Subject, Lesson, LessonStatus, LessonRequest, LessonUpdateRequest
from tutorials.forms import InvoiceForm
from tutorials.models import Invoice, LessonStatus
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Invoice, Student, LessonStatus
from django.contrib import messages

@login_required
def dashboard(request):
    current_user = request.user
    if hasattr(current_user, 'admin_profile'):
        return render(request, 'admin/admin_dashboard.html', {'user': current_user})
    if hasattr(current_user, 'tutor_profile'):
        return render(request, 'tutor/tutor_dashboard.html', {'user': current_user})
    else:
        return render(request, 'student/student_dashboard.html', {'user': current_user})

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


class ProfileUpdateView(LoginRequiredMixin, TemplateView):
    template_name = "profile.html"

    def get_context_data(self, **kwargs):
        """Add forms to the context."""
        context = super().get_context_data(**kwargs)

        if hasattr(self.request.user, 'tutor_profile'):
            tutor_form = TutorForm(instance=self.request.user.tutor_profile)
        else:
            tutor_form = None

        context['user_form'] = UserForm(instance=self.request.user)
        context['tutor_form'] = tutor_form
        return context

    def post(self, request, *args, **kwargs):
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


def requests(request):
    lesson_requests = LessonRequest.objects.all().order_by('-created')
    return render(request, 'requests.html', {'requests': lesson_requests})


class StudentsView(View):

    def get(self, request, student_id=None):
        if student_id:
            return self.student_details(request, student_id)


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
            # messages.error(request, "No valid profile for this operation.")
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
            form = UserForm(instance=entity.user)
        return render(request, self.edit, {'form': form, self.model.__name__.lower(): entity})

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
            self.status = 'admin'
        elif hasattr(request.user, 'student_profile'):
            self.list_of_lessons = Lesson.objects.filter(student=current_user.id)
            self.status = 'student'
        else:
            self.list_of_lessons = Lesson.objects.filter(tutor=current_user.id)
            self.status = 'tutor'
        return render(request, f'{self.status}/manage_lessons/lessons_list.html',
                      {"list_of_lessons": self.list_of_lessons})

    def post(self, request, lesson_id=None):

        if lesson_id:
            if 'update_feedback' in request.path:
                return self.update_feedback(request, lesson_id)
        # return redirect('lessons_details')

    def handle_lessons_form(self, request, lesson=None):
        form = LessonFeedbackForm(request.POST or None, instance=lesson)

        if request.method == "POST":
            if form.is_valid():
                try:
                    form.save()
                except:
                    form.add_error(None, "It was not possible to update this feedback")
                else:
                    path = reverse('lesson_detail', args=[lesson.lesson_id.lesson_id])
                    return HttpResponseRedirect(path)
            else:
                form = LessonFeedbackForm()

        return form

    def update_feedback(self, request, status_id=None):
        lesson = get_object_or_404(LessonStatus, pk=status_id)
        form = self.handle_lessons_form(request, lesson)

        if isinstance(form, HttpResponseRedirect):
            return form

        return render(request, 'tutor/manage_lessons/update_feedback.html', {'form': form})

    def lesson_detail(self, request, lessonStatus_id):
        """Display each lesson status for admin"""
        if lessonStatus_id:
            if 'update_feedback' in request.path:
                return self.update_feedback(request, lessonStatus_id)

        try:
            lessonStatus = LessonStatus.objects.filter(lesson_id=lessonStatus_id)
        except Exception as e:
            raise Http404(f"Could not find lesson with primary key {lessonStatus_id}")
        else:
            context = {"lessons": lessonStatus, "user": request.user}
            return render(request, 'shared/lessons/lessons_details.html', context)


class SubjectView(View):

    def get(self, request, subject_id=None):
        if subject_id:
            return self.edit_subject(request, subject_id)

        if hasattr(request.user, 'admin_profile'):
            self.list_of_subjects = Subject.objects.all()

        paginator = Paginator(self.list_of_subjects, 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        return render(request, 'admin/manage_subjects/subjects_list.html', {'page_obj': page_obj})

    def post(self, request, subject_id=None):
        if 'create' in request.path:
            return self.create_subject(request)

        if subject_id:
            if request.path.endswith('edit/'):
                return self.edit_subject(request, subject_id)
            elif request.path.endswith('delete/'):
                subject = get_object_or_404(Subject, pk=subject_id)
                return self.delete_subject(request, subject)

        # Fetch existing invoices to display
        invoices = Invoice.objects.all()
        return render(request, 'invoices/invoice_management.html', {'invoices': invoices})


        return redirect('subjects_list')

    def delete_subject(self, request, subject):
        subject.delete()
        return redirect('subjects_list')

    def handle_subject_form(self, request, subject=None):
        form = SubjectForm(request.POST or None, instance=subject)

        if request.method == "POST":
            if form.is_valid():
                try:
                    form.save()
                except:
                    form.add_error(None, "It was not possible to update this subject")
                else:
                    path = reverse('subjects_list')
                    return HttpResponseRedirect(path)
            else:
                form = SubjectForm()

        return form

    def edit_subject(self, request, subject_id):
        subject = get_object_or_404(Subject, pk=subject_id)
        form = self.handle_subject_form(request, subject)

        if isinstance(form, HttpResponseRedirect):
            return form

        return render(request, 'admin/manage_subjects/subject_edit.html', {'form': form, 'subject': subject})

    def create_subject(self, request):
        form = self.handle_subject_form(request)

        return render(request, 'admin/manage_subjects/subject_create.html', {'form': form})


class UpdateLessonRequest(View):

    def post(self, request, lesson_id=None):
        print(f"POST request received for lesson_id: {lesson_id}")  # Debug
        if lesson_id:
            if request.path.endswith('request_changes/'):
                return self.request_change(request, lesson_id)

        return redirect('lessons_list')

    def request_change(self, request, lesson_id):
        lesson = get_object_or_404(Lesson, pk=lesson_id)
        print(f"Request change for Lesson ID: {lesson_id}")  # Debug
        form = self.handle_subject_form(request, lesson)

        if isinstance(form, HttpResponseRedirect):  # Check for redirection
            return form

        return render(
            request,
            'student/manage_lessons/request_changes.html',
            {
                'form': form,
                'subject': lesson.subject_id.name,
            }
        )

    def handle_subject_form(self, request, lesson=None):

        lesson_update_instance, _ = LessonUpdateRequest.objects.get_or_create(lesson=lesson)

        form = UpdateLessonRequestForm(
            data=request.POST or None,
            instance=lesson_update_instance
        )

        if request.method == "POST":
            if form.is_valid():
                try:
                    form.save()
                    return HttpResponseRedirect(reverse('lessons_list'))
                except Exception as e:
                    form.add_error(None, f"An error occurred: {str(e)}")

        return form


class InvoiceListView(LoginRequiredMixin, View):
    def get(self, request):
        invoice_list = Invoice.objects.all().order_by('-created_at')
        paginator = Paginator(invoice_list, 10)  # Show 10 invoices per page

        page = request.GET.get('page')
        invoices = paginator.get_page(page)

        return render(request, 'invoices/invoice_list.html', {'invoices': invoices})


class CreateInvoiceView(LoginRequiredMixin, View):
    def get(self, request):
        form = InvoiceForm()
        return render(request, 'invoices/create_invoice.html', {'form': form})

    def post(self, request):
        form = InvoiceForm(request.POST)
        if form.is_valid():
            invoice = form.save(commit=False)

            # Get uninvoiced lessons for the student
            uninvoiced_lessons = LessonStatus.objects.filter(
                lesson_id__student=invoice.student,
                invoiced=False
            )

            if not uninvoiced_lessons.exists():
                messages.error(request, "No uninvoiced lessons found for this student.")
                return render(request, 'invoices/create_invoice.html', {'form': form})

            invoice.save()
            invoice.lessons.set(uninvoiced_lessons)
            messages.success(request, f"Invoice #{invoice.invoice_id} created successfully.")
            return redirect('invoice_list')

        return render(request, 'invoices/create_invoice.html', {'form': form})


class InvoiceDetailView(LoginRequiredMixin, View):
    def get(self, request, invoice_id):
        invoice = get_object_or_404(Invoice, invoice_id=invoice_id)
        return render(request, 'invoices/invoice_detail.html', {'invoice': invoice})


@login_required
def invoice_management(request):
    invoices = Invoice.objects.all().order_by('-created_at')
    return render(request, 'invoices/invoice_list.html', {'invoices': invoices})


@login_required
def create_invoice(request):
    # Print debug information about available data
    print("DEBUG: Checking for data")
    print(f"Number of students: {Student.objects.count()}")
    print(f"Number of subjects: {Subject.objects.all().count()}")

    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        if form.is_valid():
            invoice = form.save(commit=False)
            subject = form.cleaned_data['subject']
            invoice.save()

            # Link lessons
            lessons = LessonStatus.objects.filter(
                lesson_id__student=invoice.student,
                lesson_id__subject_id=subject,
                invoiced=False
            )
            if lessons.exists():
                invoice.lessons.set(lessons)
                lessons.update(invoiced=True)
                messages.success(request, f'Invoice #{invoice.id} created successfully')
            else:
                messages.warning(request, 'No uninvoiced lessons found for selected student and subject')
            return redirect('invoice_list')
        else:
            print("Form errors:", form.errors)
    else:
        form = InvoiceForm()

    return render(request, 'invoices/create_invoice.html', {'form': form})

@login_required
def invoice_list(request):
    # Make sure we're getting all related data in one query
    invoices = (Invoice.objects
                .select_related('student__user')
                .prefetch_related('lessons')
                .all()
                .order_by('-created_at'))

    return render(request, 'invoices/invoice_list.html', {
        'invoices': invoices
    })

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

def requests(request):
    lesson_requests = LessonRequest.objects.all().order_by('-created')
    return render(request, 'requests.html', {'lesson_requests': lesson_requests})

def create_lesson_request(request):
    if request.method == 'POST':
        form = LessonRequestForm(request.POST)
        if form.is_valid():
            # Create lesson request but don't save it yet
            lesson_request = form.save(commit=False)

            # Associate the logged-in student's profile with the lesson request
            lesson_request.student = request.user.student_profile

            # Save the lesson request to the database
            lesson_request.save()

            # Redirect to a success page or another page after form submission
            return redirect('lesson_request_success')
    else:
        form = LessonRequestForm()

    return render(request, 'lesson_request_form.html', {'form': form})

def lesson_request_success(request):
    return render(request, 'lesson_request_success.html')

def my_requests(request):
    my_requests = LessonRequest.objects.all().order_by('-created')
    return render(request, 'my_requests.html', {'my_requests': my_requests})

def delete_request(request, request_id):
    request = get_object_or_404(LessonRequest, pk=request_id)
    request.delete()
    return redirect('my_requests')

class StudentsView(View):

    def get(self, request, student_id=None):
        if student_id:
            return self.student_details(request, student_id)

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
    
'''
This class is to gather lessons information to present them as a calendar
'''
class Calendar(View):
    def get(self, request, year=None, month=None):
        user = request.user
        today = now().date()

        if not year or not month:
            year, month = today.year, today.month

        LessonStatus.objects.filter(date__lt=today, status='Pending').update(status='Completed')
        if hasattr(user, 'tutor_profile'):
            lessons = Lesson.objects.filter(tutor__user=user)
        elif hasattr(user, 'student_profile'):
            lessons = Lesson.objects.filter(student__user=user)
        
        first_day = datetime(year, month, 1).date()
        last_day = (first_day + timedelta(days=32)).replace(day=1) - timedelta(days=1)

        frequency_lessons = self.lessons_frequency(lessons, first_day)
        schedule = self.weekly_schedule(frequency_lessons, first_day, last_day)

        next_month = (last_day + timedelta(days=1)).replace(day=1)
        prev_month = (first_day - timedelta(days=1)).replace(day=1)

        content = {
            'schedule': schedule,
            'current_month': first_day.strftime('%B %Y'),
            'previous_month': prev_month,
            'next_month': next_month,
        }
        return render(request, 'shared/calendar.html', content)
        
    '''
    Counts the lesson prequency to present each lesson in a schedule for the user
    '''
    def lessons_frequency(self, lessons, start):
        freq = []
        for lesson in lessons:
            current_date = lesson.start_date
            end_lesson = lesson.term_id.end_date
            while current_date <= end_lesson:
                if start <= current_date <= end_lesson:
                    lesson_status = LessonStatus.objects.filter(lesson_id=lesson).first()
                    time = lesson_status.time 
                    freq.append({
                        'student': lesson.student,
                        'tutor': lesson.tutor,
                        'subject': lesson.subject_id,
                        'date': current_date,
                        'time': time,
                        'status': lesson_status.status,
                    })

                # modify the date based on lesson frequency
                if lesson.frequency == 'D':
                    current_date += timedelta(days=1)
                elif lesson.frequency == 'M':
                    current_date = (current_date.replace(day=1) + timedelta(days=32)).replace(day=lesson.start_date.day)
                else : 
                    current_date += timedelta(weeks=1)
        return freq
            

    def weekly_schedule(self, frquency_lessons, start, end):
        weekly_lessons = {}
        current_date = start
        week_start = current_date - timedelta(days=current_date.weekday())
        week_end = week_start + timedelta(days=6)

        while week_start <= end:
            week_key = f"{week_start.strftime('%b %d')} - {week_end.strftime('%b %d, %Y')}"
            weekly_lessons[week_key] = []

            for lesson in frquency_lessons:
                if week_start <= lesson['date'] <= week_end:
                    weekly_lessons[week_key].append(lesson)

            week_start += timedelta(days=7)
            week_end += timedelta(days=7)

        return weekly_lessons

    
class ViewLessons(View):

    def get(self, request, lesson_id=None):
        current_user = request.user
        if lesson_id:
            return self.lesson_detail(request, lesson_id)

        if hasattr(current_user, 'admin_profile'):
            self.list_of_lessons = Lesson.objects.all()
            self.status = 'admin'
        elif hasattr(request.user, 'student_profile'):
            self.list_of_lessons = Lesson.objects.filter(student=current_user.id)
            self.status = 'student'
        else:
            self.list_of_lessons = Lesson.objects.filter(tutor=current_user.id)
            self.status = 'tutor'
        return render(request, f'{self.status}/manage_lessons/lessons_list.html', {"list_of_lessons": self.list_of_lessons})

    def post(self, request, lesson_id=None):

        if lesson_id:
            if 'update_feedback' in request.path:
                return self.update_feedback(request, lesson_id)
        #return redirect('lessons_details')

    def handle_lessons_form(self, request, lesson=None):
        form = LessonFeedbackForm(request.POST or None, instance=lesson)

        if request.method == "POST":
            if form.is_valid():
                try:
                    form.save()
                except:
                    form.add_error(None, "It was not possible to update this feedback")
                else:
                    path = reverse('lesson_detail', args=[lesson.lesson_id.lesson_id])
                    return HttpResponseRedirect(path)
            else:
                form = LessonFeedbackForm()

        return form

    def update_feedback(self, request, status_id=None):
        lesson = get_object_or_404(LessonStatus, pk=status_id)
        form = self.handle_lessons_form(request, lesson)

        if isinstance(form, HttpResponseRedirect):
            return form

        return render(request, 'tutor/manage_lessons/update_feedback.html', {'form': form})

    def lesson_detail(self, request, lessonStatus_id):
        """Display each lesson status for admin"""
        if lessonStatus_id:
            if 'update_feedback'in request.path:
                return self.update_feedback(request, lessonStatus_id)

        try:
            lessonStatus = LessonStatus.objects.filter(lesson_id=lessonStatus_id)
        except Exception as e:
            raise Http404(f"Could not find lesson with primary key {lessonStatus_id}")
        else:
            context = {"lessons": lessonStatus, "user": request.user}
            return render(request, 'shared/lessons/lessons_details.html', context)

class SubjectView(View):

    def get(self, request, subject_id=None):
        if subject_id:
            return self.edit_subject(request, subject_id)

        if hasattr(request.user, 'admin_profile'):
            self.list_of_subjects = Subject.objects.all()

        paginator = Paginator(self.list_of_subjects, 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        return render(request, 'admin/manage_subjects/subjects_list.html', {'page_obj': page_obj})

    def post(self, request, subject_id=None):
        if 'create' in request.path:
            return self.create_subject(request)

        if subject_id:
            if request.path.endswith('edit/'):
                return self.edit_subject(request, subject_id)
            elif request.path.endswith('delete/'):
                subject = get_object_or_404(Subject, pk=subject_id)
                return self.delete_subject(request, subject)

        return redirect('subjects_list')

    def delete_subject(self, request, subject):
        subject.delete()
        return redirect('subjects_list')

    def handle_subject_form(self, request, subject=None):
        form = SubjectForm(request.POST or None, instance=subject)

        if request.method == "POST":
            if form.is_valid():
                try:
                    form.save()
                except:
                    form.add_error(None, "It was not possible to update this subject")
                else:
                    path = reverse('subjects_list')
                    return HttpResponseRedirect(path)
            else:
                form = SubjectForm()

        return form

    def edit_subject(self, request, subject_id):
        subject = get_object_or_404(Subject, pk=subject_id)
        form = self.handle_subject_form(request, subject)

        if isinstance(form, HttpResponseRedirect):
            return form

        return render(request, 'admin/manage_subjects/subject_edit.html', {'form': form, 'subject': subject})

    def create_subject(self, request):
        form = self.handle_subject_form(request)

        return render(request, 'admin/manage_subjects/subject_create.html', {'form': form})

class UpdateLessonRequest(View):

    def post(self, request, lesson_id=None):
        print(f"POST request received for lesson_id: {lesson_id}")  # Debug
        if lesson_id:
            if request.path.endswith('request_changes/'):
                return self.request_change(request, lesson_id)

        return redirect('lessons_list')

    def request_change(self, request, lesson_id):
        lesson = get_object_or_404(Lesson, pk=lesson_id)
        print(f"Request change for Lesson ID: {lesson_id}")  # Debug
        form = self.handle_subject_form(request, lesson)

        if isinstance(form, HttpResponseRedirect):  # Check for redirection
            return form

        return render(
            request,
            'student/manage_lessons/request_changes.html',
            {
                'form': form,
                'subject': lesson.subject_id.name,
            }
        )

    def handle_subject_form(self, request, lesson=None):

        lesson_update_instance, _ = LessonUpdateRequest.objects.get_or_create(lesson=lesson)

        form = UpdateLessonRequestForm(
            data=request.POST or None,
            instance=lesson_update_instance
        )

        if request.method == "POST":
            if form.is_valid():
                try:
                    form.save()
                    return HttpResponseRedirect(reverse('lessons_list'))
                except Exception as e:
                    form.add_error(None, f"An error occurred: {str(e)}")

        return form
