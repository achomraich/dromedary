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
from tutorials.forms import LogInForm, PasswordForm, UserForm, SignUpForm, SubjectForm, LessonFeedbackForm, UpdateLessonRequestForm, UpdateLessonForm
from tutorials.helpers import login_prohibited
from django.core.paginator import Paginator
from .models import Invoice
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from tutorials.models import Student, Admin, Tutor, Subject, Lesson, LessonStatus, LessonRequest, LessonUpdateRequest, Status
from django.db.models import Q, Exists, OuterRef
import datetime
from django.utils.timezone import now
from dateutil.relativedelta import relativedelta

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



