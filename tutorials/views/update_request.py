from datetime import datetime

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views import View

from tutorials.forms import UpdateLessonRequestForm, UpdateLessonForm
from tutorials.helpers import TutorAvailabilityManager
from tutorials.models import LessonUpdateRequest, Lesson, LessonStatus, Status, Tutor

from django.utils.timezone import now
from datetime import timedelta, datetime
import datetime


"""
This file contains classes to handle 
1- Update lesson request
2- Update lessons 
"""

class UpdateLessonRequest(LoginRequiredMixin, View):
    """ Update the lesson request by admin or user"""
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
        """ Allows the user to request changes """
        lesson = get_object_or_404(Lesson, pk=lesson_id)
        form = self.handle_subject_form(request, lesson)

        if isinstance(form, HttpResponseRedirect):
            return form

        return render(
            request,
            'student/manage_lessons/request_changes.html',
            {
                'form': form,
                'subject': lesson.subject.name,
            }
        )

    def handle_subject_form(self, request, lesson=None):
            """Handels the subject form"""
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

                    Lesson.objects.filter(id=lesson.id).update(notes=f'Requested by {saved_instance.made_by}: {saved_instance.get_update_option_display()}')
                    saved_instance.save()
                    self.change_status(saved_instance)
                except Exception as e:
                    form.add_error(None, f"An error occurred: {str(e)}")
                else:
                    return HttpResponseRedirect(reverse('lessons_list'))

            return form

    def change_status(self, saved_instance):
        """Changes the status of lesson"""
        if saved_instance and saved_instance.lesson:
            try:
                lesson = saved_instance.lesson

                LessonStatus.objects.filter(
                    status=Status.SCHEDULED,
                    lesson_id=lesson
                ).update(status=Status.PENDING)
            except Exception as e:
                print(f"Error in changing status: {e}")


class UpdateLesson(LoginRequiredMixin, View):
    """ Handeles updates related to lessons """
    def __init__(self):
        self.availability_manager = TutorAvailabilityManager()

    def get(self, request, lesson_id=None):
        return self.update_lesson(request, lesson_id)

    def post(self, request, lesson_id=None):
        if lesson_id:
            if request.path.endswith(f'update_requests/{lesson_id}/'):
                self.update_lesson(request, lesson_id)
                return redirect('update_requests')

        return redirect('update_requests')

    def update_lesson(self, request, lesson_id):
        ''' Updates lesssons '''
        option = LessonUpdateRequest.objects.get(lesson=Lesson.objects.get(pk=lesson_id), is_handled="N")
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
                'all_tutors_availability': self.availability_manager.get_all_tutor_availability(Lesson.objects.get(pk=lesson_id).subject.name),
                'update_option': option.get_update_option_display()
            }
        )

    def cancel_lesson(self, request, lesson_id):
        ''' Cancels a lesson '''
        self.availability_manager.cancel_lesson_availability(lesson_id)
        messages.success(request, "Lesson cancelled successfully.")
        LessonUpdateRequest.objects.filter(lesson_id=lesson_id, is_handled="N").update(is_handled="Y")
        return redirect('lessons_list')

    def prepare_update_form(self, request, lesson_id):
        ''' Handles update lesson form '''
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

        if not first_pending_lesson:
            messages.error(request, 'No lessons to reschedule!')
            LessonUpdateRequest.objects.filter(lesson_=lesson_id, is_handled="N").update(is_handled="Y")
            Lesson.objects.filter(lesson=lesson_id).update(notes='—')
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
            return form

        return form

    def save_form_updates(self, form, lesson_id, request):
        ''' save changes '''
        saved_instance = form.save()
        new_tutor = request.POST.get('new_tutor')
        new_lesson_time = request.POST.get('new_lesson_time')

        try:
            new_day_of_week = datetime.datetime.strptime(request.POST.get('new_day_of_week'), '%Y-%m-%d').date()
        except Exception as e:
            print(e)

        try:
            tutor_availability = self.availability_manager.is_tutor_available(new_lesson_time, new_day_of_week.weekday(), Tutor.objects.get(pk=new_tutor), form.cleaned_data['duration'])
        except Exception as e:
            print(e)

        if not tutor_availability:
            form.add_error(None, 'Tutor is not available!!!')
            messages.error('Tutor is not available!!!')
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
            saved_instance.term.end_date,
            lesson_id
        )

        LessonUpdateRequest.objects.filter(lesson=lesson_id, is_handled="N").update(is_handled="Y")
        Lesson.objects.filter(id=lesson_id).update(notes='—')
