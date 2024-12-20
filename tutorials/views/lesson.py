from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import OuterRef, Exists
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.core.paginator import Paginator
from django.utils.timezone import now
from django.views import View

from tutorials.forms import LessonFeedbackForm
from tutorials.models import LessonStatus, Status, LessonUpdateRequest, Lesson


"""
This file contains classes to handle 
Lessons
"""

class ViewLessons(LoginRequiredMixin, View):
    """Allows admin and users to view list of lessons."""
    def get(self, request, lesson_id=None):
        """Handles the list of lessons."""
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
                    status=Status.SCHEDULED
                )
            )
        )

        self.list_of_lessons = self.list_of_lessons.order_by('student__user__first_name')
        paginator = Paginator(self.list_of_lessons, 20)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)

        lessons_requests = LessonUpdateRequest.objects.filter(lesson__in=self.list_of_lessons, is_handled="N")
        lessons_with_requests = set(lessons_requests.values_list('lesson_id', flat=True))

        return render(request, f'{self.status}/manage_lessons/lessons_list.html',
                      {"list_of_lessons": page_obj, 'lessons_with_requests': lessons_with_requests,
                       'can_handle_request': self.can_be_updated, 'page_obj': page_obj})

    def post(self, request, lesson_id=None):
        """Handle POST requests based on lesson actions."""
        if hasattr(request.user, 'admin_profile'):
            self.status = 'admin'
        elif hasattr(request.user, 'student_profile'):
            self.status = 'student'
        else:
            self.status = 'tutor'

        if lesson_id:
            if 'update_feedback' in request.path:
                return self.update_feedback(request, lesson_id)
            elif 'cancel_lesson' in request.path:
                return self.cancel_lesson(request, lesson_id)

        # If no lesson_id provided, redirect back to list of lessons
        return redirect('lessons_list')

    def handle_lessons_form(self, request, lesson=None):
        """Processes the form to handle lesson feedback updating."""
        form = LessonFeedbackForm(request.POST or None, instance=lesson)

        if form.is_valid():
            try:
                form.save()
            except:
                form.add_error(None, "It was not possible to update this feedback")
            else:
                path = reverse('lesson_detail', args=[lesson.lesson_id.id])
                return HttpResponseRedirect(path)
        else:
            form = LessonFeedbackForm(instance=lesson)

        return form

    def update_feedback(self, request, status_id=None):
        """Allows tutor to update the feedback."""
        lesson = get_object_or_404(LessonStatus, pk=status_id)
        form = self.handle_lessons_form(request, lesson)

        if isinstance(form, HttpResponseRedirect):
            return form

        return render(request, 'tutor/manage_lessons/update_feedback.html', {'form': form})

    def cancel_lesson(self, request, status_id=None):
        """Allows cancelling a lesson."""
        lesson = get_object_or_404(LessonStatus, pk=status_id)
        if lesson.status == Status.SCHEDULED:
            lesson.status = Status.CANCELLED
            lesson.save()
        lesson.feedback = f'Lesson was cancelled by {self.status}'
        lesson.save()

        return redirect('lesson_detail', lesson_id=LessonStatus.objects.get(pk=status_id).lesson_id.id)

    def lesson_detail(self, request, lessonStatus_id):
        """Views the lesson details/each lesson scheduled."""
        if hasattr(request.user, 'admin_profile'):
            self.status = 'admin'
        elif hasattr(request.user, 'student_profile'):
            self.status = 'student'
        else:
            self.status = 'tutor'

        if lessonStatus_id:
            if 'update_feedback' in request.path:
                return self.update_feedback(request, lessonStatus_id)
            if 'cancel_lesson' in request.path:
                return self.cancel_lesson(request, lessonStatus_id)

        try:
            lessonStatus = LessonStatus.objects.filter(lesson_id=lessonStatus_id)
        except Exception as e:
            raise Http404(f"Could not find lesson with primary key {lessonStatus_id}")
        else:
            context = {"lessons": lessonStatus, "user": request.user}
            return render(request, 'shared/lessons/lessons_details.html', context)
