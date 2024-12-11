from datetime import datetime

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views import View

from tutorials.forms import UpdateLessonRequestForm, UpdateLessonForm
from tutorials.helpers import TutorAvailabilityManager
from tutorials.models import LessonUpdateRequest, Lesson, LessonStatus, Status


class UpdateLessonRequest(LoginRequiredMixin, View):


    def get(self, request, lesson_id=None):
        current_user = request.user
        if hasattr(current_user, 'admin_profile'):
            list_of_requests = LessonUpdateRequest.objects.all()
        elif hasattr(current_user, 'student_profile') or hasattr(current_user, 'tutor_profile'):
            return self.request_change(request, lesson_id)
        else:
            return reverse('log_in')

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
                'subject': lesson.subject,
            }
        )

    def handle_subject_form(self, request, lesson=None):
        #if request.method == "POST":

            lesson_update_instance = LessonUpdateRequest(lesson=lesson)

            form = UpdateLessonRequestForm(
                data=request.POST if request.method == "POST" else None,
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


class UpdateLesson(LoginRequiredMixin, View):
    def __init__(self):
        self.availability_manager = TutorAvailabilityManager()

    def get(self, request, lesson_id=None):
        print(lesson_id)

        return self.update_lesson(request, lesson_id)

    def post(self, request, lesson_id=None):
        if lesson_id:
            if request.path.endswith(f'update_requests/{lesson_id}/'):
                self.update_lesson(request, lesson_id)
                return redirect('update_requests')

        return redirect('update_requests')

    def update_lesson(self, request, lesson_id):
        option = LessonUpdateRequest.objects.get(lesson_id=lesson_id, is_handled="N")
        lesson = get_object_or_404(Lesson, pk=lesson_id)

        if option.update_option == '3':
            return self.cancel_lesson(request, lesson_id=lesson_id)
        elif option.update_option in ['1', '2']:
            form = self.prepare_update_form(request, lesson_id)
            if not form:
                return redirect('update_requests')

        return render(
            request,
            'admin/manage_update_requests/update_lesson.html',
            {
                'form': form,
                'current_tutor_availability': self.availability_manager.get_current_tutor_availability(lesson_id),
                'all_tutors_availability': self.availability_manager.get_all_tutor_availability(),
                'update_option': option.get_update_option_display()
            }
        )

    def cancel_lesson(self, request, lesson_id):
        self.availability_manager.cancel_lesson_availability(lesson_id)
        messages.success(request, "Lesson cancelled successfully.")
        LessonUpdateRequest.objects.filter(lesson_id=lesson_id, is_handled="N").update(is_handled="Y")
        return redirect('lessons_list')

    def prepare_update_form(self, request, lesson_id):
        lesson_update_instance = get_object_or_404(Lesson, pk=lesson_id)
        update_option_display = LessonUpdateRequest.objects.get(lesson_id=lesson_id, is_handled="N").get_update_option_display()
        details = LessonUpdateRequest.objects.get(lesson_id=lesson_id, is_handled="N").details
        lesson_time = LessonStatus.objects.filter(lesson_id=lesson_update_instance, date__gt=now()).first()
        next_lesson_date = LessonStatus.objects.filter(lesson_id=lesson_update_instance, status=Status.PENDING)

        if next_lesson_date:
            next_lesson_date = next_lesson_date[0]

        first_pending_lesson = LessonStatus.objects.filter(
                lesson_id=lesson_id, status=Status.PENDING
            ).order_by('date').first()
        print(first_pending_lesson.date)
        if not first_pending_lesson:
            messages.error(request, 'No lessons to reschedule!')
            LessonUpdateRequest.objects.filter(lesson_id=lesson_id, is_handled="N").update(is_handled="Y")
            Lesson.objects.filter(lesson_id=lesson_id).update(notes='—')
            return None

        form = UpdateLessonForm(
            data=request.POST if request.method == "POST" else None,
            instance=lesson_update_instance,
            update_option=update_option_display,
            details = details,
            regular_lesson_time=lesson_time.time if lesson_time else first_pending_lesson.time,
            day_of_week=self.availability_manager.get_closest_day(lesson_id=lesson_id),
            next_lesson_date=next_lesson_date.date if next_lesson_date else first_pending_lesson.date
        )

        print(form.is_valid())

        if form.is_valid():
            try:
                if request.method == "POST":
                    print('It is post method')
                    self.save_form_updates(form, lesson_id, request)
            except Exception as e:
                form.add_error(None, f"An error occurred: {str(e)}")
            else:
                return HttpResponseRedirect(reverse('lessons_list'))
        else:
            print(form.errors)  # Print errors to see what's wrong
            return form

        return form

    def save_form_updates(self, form, lesson_id, request):
        saved_instance = form.save()
        new_tutor = request.POST.get('new_tutor')
        new_lesson_time = request.POST.get('new_lesson_time')
        print(new_lesson_time)
        new_day_of_week = datetime.strptime(request.POST.get('new_day_of_week'), '%Y-%m-%d').date()

        '''print(new_day_of_week)
        ta=TutorAvailability.objects.filter(tutor=new_tutor,
                                         day=new_day_of_week.weekday(),
                                         start_time__lte=new_lesson_time,
                                         end_time__gte=end_time, status='Available')
        print(ta)
        if TutorAvailability.objects.filter(tutor=new_tutor,
                                         day=new_day_of_week.weekday(),
                                         start_time__lte=new_lesson_time,
                                         end_time__gte=end_time, status='Available'):
            print('true')
            return
        else:
            print('false')
            messages.error('Tutor is not available!!!')
            return
        '''
        Lesson.objects.filter(pk=lesson_id).update(tutor=new_tutor)



        self.availability_manager.restore_old_tutor_availability(
            saved_instance.tutor,
            form.cleaned_data['next_lesson'],
            form.cleaned_data['lesson_time'],
            saved_instance.duration
        )

        self.availability_manager.update_new_tutor_availability(
            new_lesson_time,
            new_day_of_week,
            saved_instance.duration,
            new_tutor
        )

        self.availability_manager.update_lesson_statuses(
            form.cleaned_data['next_lesson'],
            new_day_of_week,
            new_lesson_time,
            saved_instance.frequency,
            saved_instance.term_id.end_date,
            lesson_id
        )
        LessonUpdateRequest.objects.filter(lesson_id=lesson_id, is_handled="N").update(is_handled="Y")
        Lesson.objects.filter(lesson_id=lesson_id).update(notes='—')