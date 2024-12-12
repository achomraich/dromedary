from django.shortcuts import render

from tutorials.models import LessonStatus, Lesson
from django.views import View

from datetime import timedelta, datetime
from django.utils.timezone import now

'''
This class is to gather lessons information to present them as a calendar
'''
class Calendar(View):
    def get(self, request, year=None, month=None):
        user = request.user
        today = now().date()

        if not year or not month:
            year, month = today.year, today.month

        year = int(request.GET.get('year', year))
        month = int(request.GET.get('month', month))

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
    Counts the lesson frequency to present each lesson in a schedule for the user
    '''

    def lessons_frequency(self, lessons, start):
        freq = []
        for lesson in lessons:
            current_date = lesson.start_date
            end_lesson = lesson.term.end_date
            while current_date <= end_lesson:
                if start <= current_date <= end_lesson:
                    lesson_status = LessonStatus.objects.filter(lesson_id=lesson).first()
                    time = lesson_status.time

                    if lesson_status:
                        freq.append({
                            'student': lesson.student,
                            'tutor': lesson.tutor,
                            'subject': lesson.subject,
                            'date': current_date,
                            'time': time,
                            'status': lesson_status.status,
                        })

                # modify the date based on lesson frequency
                if lesson.frequency == 'D':
                    current_date += timedelta(days=1)
                elif lesson.frequency == 'M':
                    current_date = (current_date.replace(day=1) + timedelta(days=32)).replace(day=lesson.start_date.day)
                else:
                    current_date += timedelta(weeks=1)
        return freq

    def weekly_schedule(self, frequency_lessons, start, end):
        weekly_lessons = {}
        current_date = start
        week_start = current_date - timedelta(days=current_date.weekday())
        week_end = week_start + timedelta(days=6)

        while week_start <= end:
            week_key = f"{week_start.strftime('%b %d')} - {week_end.strftime('%b %d, %Y')}"
            weekly_lessons[week_key] = []

            for lesson in frequency_lessons:
                if week_start <= lesson['date'] <= week_end:
                    weekly_lessons[week_key].append(lesson)

            week_start += timedelta(days=7)
            week_end += timedelta(days=7)

        return weekly_lessons