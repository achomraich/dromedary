from functools import reduce

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.db import IntegrityError

from django.http import Http404, HttpResponseForbidden, HttpResponseRedirect
from django.views import View
from django.views.generic import TemplateView, ListView
from django.views.generic.edit import FormView, UpdateView
from django.urls import reverse
from tutorials.forms import LogInForm, PasswordForm, UserForm, SignUpForm, SubjectForm, LessonFeedbackForm, \
    UpdateLessonRequestForm, LessonRequestForm, TutorForm, AssignTutorForm, TutorAvailabilityForm, InvoiceForm, \
    UpdateLessonForm

from tutorials.helpers import login_prohibited
from django.core.paginator import Paginator
from django.utils.timezone import now
from datetime import timedelta, datetime
import calendar
from .models import Invoice, Status, TutorAvailability
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404

from django.db.models import Q, Exists, OuterRef
import datetime
from dateutil.relativedelta import relativedelta

from tutorials.models import Student, Admin, Tutor, Subject, Lesson, LessonStatus, LessonRequest, LessonUpdateRequest, Status, Invoice, LessonStatus, Term
from django.utils import timezone




@login_required
def dashboard(request):
    current_user = request.user

    # Get current term
    current_term = Term.objects.filter(
        start_date__lte=timezone.now().date(),
        end_date__gte=timezone.now().date()
    ).first()

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
        if student.has_new_lesson_notification:
            messages.info(request, 'There has been an update to your lesson requests!')
            student.has_new_lesson_notification = False
            student.save()
        return render(request, 'student/student_dashboard.html', context)


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
            messages.success(request, f"Invoice #{invoice.id} created successfully.")
            return redirect('invoice_list')

        return render(request, 'invoices/create_invoice.html', {'form': form})


class InvoiceDetailView(LoginRequiredMixin, View):
    def get(self, request, invoice_id):
        invoice = get_object_or_404(Invoice, id=invoice_id)  # Changed from invoice_id to id
        return render(request, 'invoices/invoice_detail.html', {'invoice': invoice})

    def post(self, request, invoice_id):
        invoice = get_object_or_404(Invoice, id=invoice_id)
        if 'delete' in request.POST:
            invoice.delete()
            messages.success(request, f'Invoice #{invoice_id} deleted successfully')
            return redirect('invoice_list')
        elif 'mark_paid' in request.POST:
            invoice.mark_as_paid()
            messages.success(request, f'Invoice #{invoice_id} marked as paid')
            return redirect('invoice_list')
        return redirect('invoice_detail', invoice_id=invoice_id)


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

class RequestView(View):
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
            self.requests_list = LessonRequest.objects.filter(student=current_user.id)
            self.status = 'student'
        return render(request, f'{self.status}/requests/requests.html', {"lesson_requests": self.requests_list})

    def post(self, request, *args, **kwargs):
        lrequest_id = request.POST.get('request_id')
        if not lrequest_id:
            messages.error(request, "No entity ID provided for the operation.")
            return redirect('requests')

        lrequest = get_object_or_404(LessonRequest, request_id=lrequest_id)

        if 'edit' in request.POST:
            return self.assign_tutor(request, lrequest)
        elif 'reject' in request.POST:
            return self.reject_request(request, lrequest)
        elif 'cancel' in request.POST:
            return self.cancel_request(request, lrequest)

        messages.error(request, "Invalid operation.")
        return redirect('requests')

    def request_assign(self, request, request_id, form=None):
        lrequest = get_object_or_404(LessonRequest, request_id=request_id)
        lrequest.refresh_from_db()

        if not form:
            form = AssignTutorForm()

        return render(request, 'admin/requests/assign_tutor.html', {'form' : form, 'request': lrequest})

    def assign_tutor(self, request, lrequest):

        form = AssignTutorForm(request.POST)

        if form.is_valid():
            tutor = form.cleaned_data['tutor']
            start_date = form.cleaned_data['start_date']
            price_per_lesson = form.cleaned_data['price_per_lesson']

            # Create a new Lesson based on the form data and LessonRequest details
            Lesson.objects.create(
                tutor=tutor,
                student=lrequest.student,
                subject_id=lrequest.subject,
                term_id=lrequest.term,
                frequency="W",  # Assuming "W" for weekly frequency, can be updated if needed
                duration=lrequest.duration,  # Duration from the LessonRequest
                start_date=start_date,
                price_per_lesson=price_per_lesson,
            )

            lrequest.status = Status.CONFIRMED
            lrequest.save()

            messages.success(request, "Request assigned successfully.")

            return redirect('requests')
        else:
            print("Form errors:", form.errors.as_data())
            messages.error(request, "Failed to update details. Please correct the errors and try again.")
            lrequest.refresh_from_db()
            return self.request_assign(request, lrequest.request_id, form)

    def reject_request(self, request, lrequest):
        lrequest.status = Status.REJECTED
        lrequest.save()
        messages.success(request, "Request rejected.")
        return redirect('requests')

    def cancel_request(self, request, lrequest):
        lrequest.status = Status.CANCELLED
        lrequest.save()
        messages.success(request, "Request cancelled.")
        return redirect('requests')

class MakeRequestView(View):

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
            return redirect('dashboard')
        else:
            messages.error(request, "Failed to update details. Please correct the errors and try again.")

        return render(request, 'student/requests/lesson_request_form.html', {'form': form})

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

        first_day = datetime.datetime(year, month, 1).date()
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
        self.can_be_updated = []
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

        self.can_be_updated = self.list_of_lessons.filter(
            Exists(
                LessonStatus.objects.filter(
                    lesson_id=OuterRef('pk'),
                    status=Status.BOOKED
                )
            )
        )
        print(self.can_be_updated)

        lessons_requests = LessonUpdateRequest.objects.filter(lesson__in=self.list_of_lessons, is_handled="N")
        lessons_with_requests = set(lessons_requests.values_list('lesson_id', flat=True))

        '''message = {
            request.lesson_id: {
                "update_option": request.get_update_option_display(),
                "made_by": request.made_by
            }
            for request in lessons_requests
        }'''
        return render(request, f'{self.status}/manage_lessons/lessons_list.html', {"list_of_lessons": self.list_of_lessons, 'lessons_with_requests': lessons_with_requests, 'can_handle_request': self.can_be_updated})

    def post(self, request, lesson_id=None):

        if lesson_id:
            if 'update_feedback' in request.path:
                return self.update_feedback(request, lesson_id)
            elif 'cancel_lesson' in request.path:
                return self.cancel_lesson(request, lesson_id)

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

    def cancel_lesson(self, request, status_id=None):

        lesson = get_object_or_404(LessonStatus, pk=status_id)
        if lesson.status == Status.BOOKED:
            lesson.status = Status.CANCELLED
            lesson.save()
        lesson.feedback = f'Lesson was cancelled by {self.status}'
        lesson.save()

        return redirect('lesson_detail', lesson_id=LessonStatus.objects.get(pk=status_id).lesson_id.lesson_id)

    def lesson_detail(self, request, lessonStatus_id):

        if hasattr(request.user, 'admin_profile'):
            self.status = 'admin'
        elif hasattr(request.user, 'student_profile'):
            self.status = 'student'
        else:
            self.status = 'tutor'

        if lessonStatus_id:
            if 'update_feedback'in request.path:
                return self.update_feedback(request, lessonStatus_id)
            if 'cancel_lesson'in request.path:
                return self.cancel_lesson(request, lessonStatus_id)

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

    def get(self, request):
        current_user = request.user
        if hasattr(current_user, 'admin_profile'):
            list_of_requests = LessonUpdateRequest.objects.all()
        else:
            return HttpResponseRedirect('dashboard')

        return render(request, 'admin/manage_update_requests/update_lesson_request_list.html', {'list_of_requests': list_of_requests})

    def post(self, request, lesson_id=None):
        if lesson_id:
            if request.path.endswith('request_changes/'):
                return self.request_change(request, lesson_id)

        return redirect('lessons_list')

    def request_change(self, request, lesson_id):
        lesson = get_object_or_404(Lesson, pk=lesson_id)
        form = self.handle_subject_form(request, lesson)

        if isinstance(form, HttpResponseRedirect):
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
        if request.method == "POST":
            try:
                lesson_update_instance = LessonUpdateRequest.objects.get(lesson=lesson)
            except LessonUpdateRequest.DoesNotExist:
                lesson_update_instance = LessonUpdateRequest(lesson=lesson)

            form = UpdateLessonRequestForm(
                data=request.POST,
                instance=lesson_update_instance,
                user_role=request.user
            )

            if form.is_valid():
                try:
                    saved_instance = form.save()
                    if hasattr(request.user, 'tutor_profile'):
                        saved_instance.made_by = 'Tutor'
                    elif hasattr(request.user, 'student_profile'):
                        saved_instance.made_by = 'Student'

                    Lesson.objects.filter(lesson_id=lesson.lesson_id).update(notes=f'Requested by {saved_instance.made_by}: {saved_instance.get_update_option_display()}')
                    saved_instance.save()
                    self.change_status(saved_instance)
                except Exception as e:
                    form.add_error(None, f"An error occurred: {str(e)}")
                else:
                    return HttpResponseRedirect(reverse('lessons_list'))

        return form

    def change_status(self, saved_instance):
        """
        Update the lesson's status
        """
        if saved_instance and saved_instance.lesson:
            try:
                lesson = saved_instance.lesson
                print(f"Changing status for lesson {lesson.lesson_id} to 'Pending Update'")

                LessonStatus.objects.filter(
                    status=Status.BOOKED,
                    lesson_id=lesson
                ).update(status=Status.PENDING)
            except Exception as e:
                print(f"Error in changing status: {e}")

class UpdateLesson(View):

    def get(self, request, lesson_id=None):
        print(lesson_id)
        return self.update_lesson(request, lesson_id)

    def post(self, request, lesson_id=None):
        print('Y')
        if lesson_id:
            if request.path.endswith(f'update_requests/{lesson_id}/'):
                print('Y')
                return self.update_lesson(request, lesson_id)

        return redirect('update_requests')

    def update_lesson(self, request, lesson_id):
        option = LessonUpdateRequest.objects.get(lesson_id=lesson_id, is_handled="N").update_option
        lesson = get_object_or_404(Lesson, pk=lesson_id)
        print(option)
        if option == '3':
            return self.cancell_lesson(request, lesson_id=lesson_id)
        elif option == '2':
            print('Y')
            form = self.update_day_or_time(request, lesson_id=lesson_id)
        else:
            form = self.handle_update_lesson_form(request, option, lesson)

            if isinstance(form, HttpResponseRedirect):
                return form

        return render(
            request,
            'admin/manage_update_requests/update_lesson.html',
            {
                'form': form
            }
        )

    def cancell_lesson(self, request, lesson_id=None):
        current_datetime = now()

        planned_lessons = LessonStatus.objects.filter(
            Q(date__gt=current_datetime.date()) |
            Q(date=current_datetime.date(), time__gte=current_datetime.time()),
            lesson_id=lesson_id
        )
        for lesson in planned_lessons:
            lesson.status = Status.CANCELLED
            lesson.save()

        Lesson.objects.filter(
            lesson_id=lesson_id
        ).update(notes=f"All the lessons were cancelled on {current_datetime.date()}.")

        messages.success(request, "Lesson cancelled successfully.")

        LessonUpdateRequest.objects.filter(lesson_id=lesson_id, is_handled="N").update(is_handled="Y")
        return redirect('lessons_list')

    def get_closest_day(self, lesson_id=None):

        current_datetime = now()
        last_date = LessonStatus.objects.filter(date__lt=current_datetime, lesson_id=lesson_id).order_by('-date').first()

        if last_date:
            print("Last date before the given day:", last_date.date)
        else:
            print("No dates found before the given day.")
        day_name = last_date.date.strftime("%A")

        # Output the name of the day
        print("Day of the week (name):", day_name)
        return day_name

    def update_day_or_time(self, request,  lesson_id=None):
        if request.method == "POST":
            try:
                lesson_update_instance = Lesson.objects.get(lesson_id=lesson_id)
            except Lesson.DoesNotExist:
                raise Http404()
            #print(lesson_update_instance.subject_id.name)
            details = LessonUpdateRequest.objects.get(lesson_id=lesson_id).details
            update_option_display = LessonUpdateRequest.objects.get(lesson_id=lesson_id).get_update_option_display()
            print(update_option_display)
            lesson_time = LessonStatus.objects.filter(lesson_id=lesson_id, date__gt=now())
            print(lesson_time)
            if len(lesson_time) == 0:
                return Http404("No future lessons!!!")
            print(lesson_time[0].time)

            form = UpdateLessonForm(
                data=request.POST if request.method == "POST" else None,
                instance=lesson_update_instance,
                update_option=update_option_display,
                details=details,
                regular_lesson_time=lesson_time[0].time,
                day_of_week=self.get_closest_day(lesson_id=lesson_id)  # You can set this dynamically based on the lesson
            )

            if form.is_valid():
                try:
                    print("Form is valid!")
                    saved_instance = form.save()
                    print(saved_instance)
                    #saved_instance.save()

                    new_day_of_week = datetime.datetime.strptime(request.POST.get('new_day_of_week'), '%Y-%m-%d').date()
                    new_lesson_time = request.POST.get('new_lesson_time')
                    print(type(new_day_of_week))
                    #self.update_lesson_statuses(request, new_day_of_week, new_lesson_time,saved_instance.frequency,saved_instance.term_id.end_date, lesson_id)

                    # Additional processing if required
                except Exception as e:
                    form.add_error(None, f"An error occurred: {str(e)}")
                else:
                    return HttpResponseRedirect(reverse('lessons_list'))


        else:
            # For GET requests, initialize the form without POST data
            form = UpdateLessonForm(
                data=request.POST if request.method == "POST" else None,
                instance=lesson_update_instance,
                update_option=update_option_display,
                details=details,
                regular_lesson_time=lesson_time,
                day_of_week="Monday"  # You can set this dynamically based on the lesson
            )

        return form

    def update_lesson_statuses(self, request, next_lesson_date, time, frequency, end_date, lesson_id=None):
        #LessonStatus.objects.filter(date__gt=now()).delete()
        current_date=next_lesson_date
        while current_date < end_date:
            # Create a new lesson entry for the current date
            lesson = LessonStatus(lesson_id=Lesson.objects.get(pk=lesson_id), date=current_date, time=time, status='Booked', feedback="")
            lesson.save()
            print(lesson)

            # Increment the date based on the frequency
            if frequency == 'W':
                current_date += datetime.timedelta(weeks=1)
            elif frequency == 'M':
                current_date += relativedelta(months=1)
            else:
                raise ValueError("Frequency should be 'month' or 'week'.")

    '''def handle_update_lesson_form(self, request, update_option, lesson=None):
        if request.method == "POST":
            try:
                lesson_update_instance = Lesson.objects.get(lesson_id=lesson.lesson_id)
            except LessonUpdateRequest.DoesNotExist:
                Http404()

            details = LessonUpdateRequest.objects.get(lesson_id=lesson.lesson_id).details
            update_option = LessonUpdateRequest.objects.get(lesson_id=lesson).get_update_option_display()
            request_instance = get_object_or_404(LessonUpdateRequest, lesson=lesson)
            lesson_time=LessonStatus.objects.filter(lesson_id=lesson)[0].time
            #print(str(lesson_time)) #return <class 'str'>
            if isinstance(lesson_time, datetime.timedelta):
                total_seconds = int(lesson_time.total_seconds())
                hours, remainder = divmod(total_seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                lesson_time_str = f"{hours:02}:{minutes:02}:{seconds:02}"
            else:
                lesson_time_str = str(lesson_time)

            #print(type(lesson_time_str))

            form = UpdateLessonForm(
                data=request.POST,
                instance=lesson_update_instance,
                update_option=update_option,
                details=details,
                regular_lesson_time=lesson_time_str,
                day_of_week='Monday'
            )

            if form.is_valid():
                try:
                    print('is_valid')
                    #saved_instance = form.save()
                    #self.change_status(saved_instance)
                except Exception as e:
                    form.add_error(None, f"An error occurred: {str(e)}")
                else:
                    return HttpResponseRedirect(reverse('lessons_list'))

        return form'''

    def handle_update_lesson_form(self, request, update_option, lesson=None):
        if request.method == "POST":
            try:
                lesson_update_instance = Lesson.objects.get(lesson_id=lesson.lesson_id)
            except Lesson.DoesNotExist:
                raise Http404()

            details = LessonUpdateRequest.objects.get(lesson_id=lesson.lesson_id).details
            update_option_display = LessonUpdateRequest.objects.get(lesson_id=lesson).get_update_option_display()
            lesson_time = LessonStatus.objects.filter(lesson_id=lesson)[0].time

            # Convert lesson_time to string if it's a timedelta
            if isinstance(lesson_time, datetime.timedelta):
                total_seconds = int(lesson_time.total_seconds())
                hours, remainder = divmod(total_seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                lesson_time_str = f"{hours:02}:{minutes:02}:{seconds:02}"
            else:
                lesson_time_str = str(lesson_time)

            # Create the form with the appropriate data
            form = UpdateLessonForm(
                data=request.POST if request.method == "POST" else None,
                instance=lesson_update_instance,
                update_option=update_option_display,
                details=details,
                regular_lesson_time=lesson_time_str,
                day_of_week="Monday"  # You can set this dynamically based on the lesson
            )

            if form.is_valid():
                try:
                    print("Form is valid!")
                    saved_instance = form.save()
                    saved_instance.save()
                    # Additional processing if required
                    new_day_of_week = request.POST.get('new_day_of_week')
                    print(new_day_of_week)
                except Exception as e:
                    form.add_error(None, f"An error occurred: {str(e)}")
                else:
                    return HttpResponseRedirect(reverse('lessons_list'))

        else:
            # For GET requests, initialize the form without POST data
            form = UpdateLessonForm(
                instance=lesson,
                update_option=update_option,
                details=details,
                regular_lesson_time=lesson_time_str,
                day_of_week="Monday"  # You can set this dynamically based on the lesson
            )

        return form

class AvailabilityView(ListView):
    model = TutorAvailability
    template_name = 'tutor/my_availability/availabilities.html'
    context_object_name = 'availabilities'

    def get_queryset(self):
        # Filter availabilities for the logged-in tutor
        return TutorAvailability.objects.filter(tutor=self.request.user.tutor_profile)

    def post(self, request, *args, **kwargs):
        if 'remove' in request.POST:
            availability_id = request.POST.get('availability')
            try:
                availability = TutorAvailability.objects.get(id=availability_id)
                availability.delete()
                messages.success(request, "Deleted successfully.")
            except TutorAvailability.DoesNotExist:
                messages.error(request, "The selected availability does not exist.")
            return redirect('availability')


class AddEditAvailabilityView(View):
    def get(self, request, pk=None, *args, **kwargs):
        if pk:
            availability = get_object_or_404(TutorAvailability, pk=pk)
            form = TutorAvailabilityForm(instance=availability)
        else:
            form = TutorAvailabilityForm()
        return render(request, 'tutor/my_availability/add_edit_availability.html', {'form': form, 'pk': pk})

    def post(self, request, pk=None, *args, **kwargs):
        if pk:
            availability = get_object_or_404(TutorAvailability, pk=pk)
            form = TutorAvailabilityForm(request.POST, instance=availability)
        else:
            form = TutorAvailabilityForm(request.POST)

        if form.is_valid():
            availability = form.save(commit=False)
            availability.tutor = request.user.tutor_profile
            availability.save()
            messages.success(request, "Availability saved successfully.")
            return redirect('availability')
        else:
            messages.error(request, "Failed to save availability. Please correct the errors and try again.")
        return render(request, 'tutor/my_availability/add_edit_availability.html', {'form': form, 'pk': pk})