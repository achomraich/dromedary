import datetime
from datetime import timedelta
from functools import reduce

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import redirect, get_object_or_404, render
from django.utils.timezone import now
from django.views import View

from tutorials.forms import UserForm
from tutorials.models import Subject, Lesson, Student, TutorAvailability, LessonStatus, Tutor
from tutorials.views import Calendar


class EntityView(LoginRequiredMixin, View):
    model = None
    list_admin = None
    list_user = None
    details = None
    edit = None
    redirect_url = None

    def get(self, request, *args, **kwargs):
        entity_id = kwargs.get('tutor_id') or kwargs.get('student_id')
        if entity_id:
            if request.resolver_match.url_name == 'student_calendar' or request.resolver_match.url_name == 'tutor_calendar':
                return self.get_calendar(request, entity_id)
            elif request.resolver_match.url_name == 'student_details' or request.resolver_match.url_name == 'tutor_details':
                return self.entity_details(request, entity_id)

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
        availability = None
        subjects = None
        tutors = None
        students = None

        if isinstance(entity, Student):
            lessons = Lesson.objects.filter(student=entity).select_related(
                'tutor', 'subject', 'term'
            ).order_by('subject__name')
            subjects = lessons.values_list('subject__name', flat=True).distinct()
            tutors = ', '.join(sorted(tutor.user.full_name() for tutor in set(lesson.tutor for lesson in lessons)))

        else:
            lessons = Lesson.objects.filter(tutor=entity).order_by('student__user__username')
            students = ', '.join(
                sorted(student.user.full_name() for student in set(lesson.student for lesson in lessons)))
            availability = TutorAvailability.objects.filter(tutor=entity).order_by('day')
            print(availability)

        content = {
            self.model.__name__.lower(): entity,
            'lessons': lessons,
            'tutors': tutors,
            'students': students,
            'availabilities': availability,
            'subjects': subjects
        }

        if request.path.endswith('edit/'):
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
            messages.error(request, "Failed to update details. Please correct the errors and try again.")

        return self.edit_form(request, entity, form)

    def delete_entity(self, request, entity):
        entity.user.delete()
        messages.success(request, "Deleted successfully.")
        return redirect(self.redirect_url)

    def get_calendar(self, request, entity_id):
        """
        Generates a calendar view for the given entity.
        """
        entity = get_object_or_404(self.model, user__id=entity_id)
        today = now().date()
        year = int(request.GET.get('year', today.year))
        month = int(request.GET.get('month', today.month))
        LessonStatus.objects.filter(date__lt=today, status='Pending').update(status='Completed')

        if isinstance(entity, Student):
            lessons = Lesson.objects.filter(student=entity)
        elif isinstance(entity, Tutor):
            lessons = Lesson.objects.filter(tutor=entity)

        first_day = datetime.date(year, month, 1)
        last_day = (first_day + timedelta(days=32)).replace(day=1) - timedelta(days=1)

        calendar = Calendar()
        frequency_lessons = calendar.lessons_frequency(lessons, first_day)
        schedule = calendar.weekly_schedule(frequency_lessons, first_day, last_day)

        next_month = (last_day + timedelta(days=1)).replace(day=1)
        prev_month = (first_day - timedelta(days=1)).replace(day=1)

        content = {
            'schedule': schedule,
            'current_month': first_day.strftime('%B %Y'),
            'previous_month': prev_month,
            'next_month': next_month,
        }
        return render(request, 'shared/calendar.html', content)


class StudentsView(EntityView, LoginRequiredMixin):
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
            filtered_lessons = Lesson.objects.filter(subject__name=subject_filter)
            entity_list = entity_list.filter(user_id__in=filtered_lessons.values('student_id')).distinct()
        return entity_list


class TutorsView(EntityView, LoginRequiredMixin):
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
            filtered_lessons = Lesson.objects.filter(subject__name=subject_filter)
            entity_list = entity_list.filter(user_id__in=filtered_lessons.values('tutor_id')).distinct()
        return entity_list