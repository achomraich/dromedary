from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import redirect, render, get_object_or_404
from django.http import Http404, HttpResponseForbidden
from django.views import View
from django.views.generic.edit import FormView, UpdateView
from django.urls import reverse
from tutorials.forms import LogInForm, PasswordForm, UserForm, SignUpForm
from tutorials.helpers import login_prohibited
from django.core.paginator import Paginator

from tutorials.models import Student, Admin, Tutor
from tutorials.models import Lesson, LessonStatus, Tutor

@login_required
def dashboard(request):
    """Display the current user's dashboard."""
    current_user = request.user
    return render(request, 'dashboard.html', {'user': current_user})

def admin_dashboard(request):
    current_user = request.user
    return render(request, 'admin/admin_dashboard.html', {'user': current_user})

def tutor_dashboard(request):
    current_user = request.user
    return render(request, 'tutor/tutor_dashboard.html', {'user': current_user})

def student_dashboard(request):
    current_user = request.user
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
            if hasattr(user, 'admin_profile'):
                return redirect('admin_dashboard')
            elif hasattr(user, 'tutor_profile'):
                return redirect('tutordashboard')
            elif hasattr(user, 'student_profile'):
                return redirect('student_dashboard')
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

class StudentsView(View):

    def get(self, request, student_id=None):
        if student_id:
            return self.student_details(request, student_id)
        else:
            return self.get_students_list(request)
        
    def post(self, request, student_id=None):
        if student_id:
            student = get_object_or_404(Student, user__id=student_id)

            if 'edit' in request.POST:
                return self.edit_student(request, student)
            elif 'delete' in request.POST:
                return self.delete_student(request, student)

        return redirect('students_list')

    def get_students_list(self, request):
        students_list = Student.objects.all()
        paginator = Paginator(students_list, 20)

        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return render(request, 'admin/students/students_list.html', {'page_obj': page_obj})

    def student_details(self, request, student_id):
        student = get_object_or_404(Student, user__id=student_id)

        if request.path.endswith('edit/'):
            return self.edit_form(request, student)
        else:
            return render(request, 'admin/students/student_details.html', {'student' : student})
        
    def edit_form(self, request, student):
        form = UserForm(instance=student.user)
        return render(request, 'admin/students/edit_student.html', {'form' : form})
    
    def edit_student(self, request, student):
        form = UserForm(request.POST, instance=student.user)

        if form.is_valid():
            form.save()
            print("updated")
            messages.success(request, "Student details updated successfully.")
            return redirect('student_details', student_id=student.user.id)
        else:
            return self.edit_form(request, student)
    
    def delete_student(self, request, student):
        student.delete()
        print("deleted")
        messages.success(request, "Student deleted successfully.")
        return redirect('students_list')

class ViewLessons(View):

    def get(self, request, lesson_id=None):
        current_user = request.user
        if lesson_id:
            return self.lesson_detail(request, lesson_id)
        if hasattr(current_user, 'admin_profile'):
            return self.admin_lessons_list(request)
        else:
            return self.lessons_list(request, request.user.id)

    def lessons_list(self, request, user_id):
        """Display lessons for admin"""
        if hasattr(request.user, 'student_profile'):
            self.list_of_lessons = Lesson.objects.filter(student=user_id)
        else:
            self.list_of_lessons = Lesson.objects.filter(tutor=user_id)

        return render(request, 'lessons_list.html', {"list_of_lessons": self.list_of_lessons})

    def admin_lessons_list(self, request):
        """Display lessons for admin"""
        #print("problem")
        list_of_lessons = Lesson.objects.all()
        #print(list_of_lessons)
        return render(request, 'lessons_list.html', {"list_of_lessons": list_of_lessons})

    def lesson_detail(self, request, lesson_id):
        """Display each lesson status for admin"""
        try:
            lessonStatus = LessonStatus.objects.filter(lesson_id=lesson_id)
        except Exception as e:
            raise Http404(f"Could not find lesson with primary key {lesson_id}")
        else:
            context = {"lessons": lessonStatus}
            return render(request, 'lessons_details.html', context)



class AdminTutors(View):
    def get(self, request):
        return self.tutors_list(request)

    def tutors_list(self, request):
        """Display tutors for admin"""
        list_of_tutors = Tutor.objects.all()
        context = {"tutors": list_of_tutors}
        return render(request, 'tutors_list.html', context)
