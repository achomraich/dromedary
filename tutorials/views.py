from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ImproperlyConfigured
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
from tutorials.models import Student, Admin, Tutor
from tutorials.models import Lesson, LessonStatus, Tutor

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

class StudentsView(View):

    def get(self, request, student_id=None):
        if student_id:
            return self.student_details(request, student_id)
        else:
            return self.get_students(request, request.user.id)
        
    def post(self, request, student_id=None):
        if student_id:
            student = get_object_or_404(Student, user__id=student_id)

            if 'edit' in request.POST:
                return self.edit_student(request, student)
            elif 'delete' in request.POST:
                return self.delete_student(request, student)

        return redirect('students_list')

    def get_students(self, request, tutor_id=None):
        if hasattr(request.user, 'admin_profile'):
            self.list_of_students = Student.objects.all()
        elif hasattr(request.user, 'tutor_profile'):
            lessons = Lesson.objects.filter(tutor_id=tutor_id)
            self.list_of_students = Student.objects.filter(user_id__in=lessons.values('student_id'))

        paginator = Paginator(self.list_of_students, 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        if hasattr(request.user, 'admin_profile'):
            return render(request, 'admin/manage_students/students_list.html', {'page_obj': page_obj, 'user': request.user})
        elif hasattr(request.user, 'tutor_profile'):
            return render(request, 'tutor/my_students/students_list.html', {'page_obj': page_obj, 'user': request.user})

    def student_details(self, request, student_id):
        student = get_object_or_404(Student, user__id=student_id)

        if request.path.endswith('edit/'):
            return self.edit_form(request, student)
        else:
            return render(request, 'admin/manage_students/student_details.html', {'student' : student})
        
    def edit_form(self, request, student):
        form = UserForm(instance=student.user)
        return render(request, 'admin/manage_students/edit_student.html', {'form' : form})
    
    def edit_student(self, request, student):
        form = UserForm(request.POST, instance=student.user)

        if form.is_valid():
            form.save()
            print("updated")
            messages.success(request, "Student details updated successfully.")
            return redirect('student_details', student_id=student.user.id)
        else:
            print("did not update")
            return self.edit_form(request, student)
    
    def delete_student(self, request, student):
        student.delete()
        print("deleted")
        messages.success(request, "Student deleted successfully.")
        return redirect('students_list')

class TutorsView(View):

    def get(self, request, tutor_id=None):
        if tutor_id:
            return self.tutor_details(request, tutor_id)
        else:
            return self.get_tutors(request, request.user.id)

    def post(self, request, tutor_id=None):
        if tutor_id:
            tutor = get_object_or_404(Tutor, user__id=tutor_id)

            if 'edit' in request.POST:
                return self.edit_tutor(request, tutor)
            elif 'delete' in request.POST:
                return self.delete_tutor(request, tutor)

        return redirect('tutors_list')

    def get_tutors(self, request, student_id=None):
        if hasattr(request.user, 'admin_profile'):
            self.list_of_tutors = Tutor.objects.all()
        elif hasattr(request.user, 'student_profile'):
            lessons = Lesson.objects.filter(student_id=student_id)
            self.list_of_tutors = Tutor.objects.filter(user_id__in=lessons.values('tutor_id'))

        paginator = Paginator(self.list_of_tutors, 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        if hasattr(request.user, 'admin_profile'):
            return render(request, 'admin/manage_tutors/tutors_list.html', {'page_obj': page_obj, 'user': request.user})
        elif hasattr(request.user, 'student_profile'):
            return render(request, 'student/my_tutors/tutors_list.html', {'page_obj': page_obj, 'user': request.user})

    def tutor_details(self, request, tutor_id):
        tutor = get_object_or_404(Tutor, user__id=tutor_id)

        if request.path.endswith('edit/'):
            return self.edit_tutor(request, tutor)
        else:
            return render(request, 'admin/manage_tutors/tutor_details.html', {'tutor' : tutor})

    def edit_tutor(self, request, tutor):
        if request.method == "POST":
            form = UserForm(request.POST, instance=tutor.user)
            print("form")
            if form.is_valid():
                try:
                    form.save()
                except:
                    form.add_error(None, "It was not possible to edit this user.")
                else:
                    path = reverse('tutors_list')
                    return HttpResponseRedirect(path)
        else:
            form = UserForm(instance=tutor.user)
        return render(request, 'admin/manage_tutors/edit_tutor.html', {'form' : form, 'tutor' : tutor.user})

    def delete_tutor(self, request, tutor):
        tutor.delete()
        print("deleted")
        messages.success(request, "Tutor deleted successfully.")
        return redirect('tutors_list')
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

