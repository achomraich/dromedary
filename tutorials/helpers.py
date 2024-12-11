from django.conf import settings
from django.shortcuts import redirect
from django.utils.timezone import now

from tutorials.models.models import Tutor, Lesson, LessonStatus, Status, LessonStatus, TutorAvailability
from datetime import timedelta, datetime
import datetime
from tutorials.models.choices import Days

def login_prohibited(view_function):
    """Decorator for view functions that redirect users away if they are logged in."""
    
    def modified_view_function(request):
        if request.user.is_authenticated:
            return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)
        else:
            return view_function(request)
    return modified_view_function

class TutorAvailabilityManager:
    def get_current_tutor_availability(self, lesson_id):
        current_tutor = Lesson.objects.get(pk=lesson_id).tutor
        current_tutor_availability = TutorAvailability.objects.filter(tutor=current_tutor)
        for slot in current_tutor_availability:
            slot.day = dict(Days.choices).get(int(slot.day))
        return current_tutor_availability

    def get_all_tutor_availability(self):
        all_tutors_availability = TutorAvailability.objects.filter(status='Available')
        grouped_availability = {}

        for slot in all_tutors_availability:
            day = dict(Days.choices).get(int(slot.day))
            slot.day = day
            time_range = f"{slot.start_time} - {slot.end_time}"

            if day not in grouped_availability:
                grouped_availability[day] = {}

            if time_range not in grouped_availability[day]:
                grouped_availability[day][time_range] = []

            grouped_availability[day][time_range].append(slot)

        # Order the grouped availability by day
        day_order = {day[1]: i for i, day in enumerate(Days.choices)}
        sorted_availability = {
            day: grouped_availability[day]
            for day in sorted(grouped_availability.keys(), key=lambda d: day_order[d])
        }
        return sorted_availability

    def cancel_lesson_availability(self, lesson_id):
        current_datetime = now()
        planned_lessons = LessonStatus.objects.filter(
            Q(date__gt=current_datetime.date()) |
            Q(date=current_datetime.date(), time__gte=current_datetime.time()),
            lesson_id=lesson_id
        )
        for lesson in planned_lessons:
            lesson.status = Status.CANCELLED
            lesson.save()

        Lesson.objects.filter(lesson_id=lesson_id).update(
            notes=f"All lessons were cancelled on {current_datetime.date()}."
        )

    def get_closest_day(self, lesson_id):
        current_datetime = now()
        last_date = LessonStatus.objects.filter(
            date__gt=current_datetime, lesson_id=lesson_id
        ).order_by('date').first()

        if last_date:
            return last_date.date.weekday()

        first_pending_lesson=LessonStatus.objects.filter(lesson_id=lesson_id, status=Status.PENDING).order_by('date').last()
        if first_pending_lesson and Lesson.objects.get(pk=first_pending_lesson.lesson_id.lesson_id).term_id.end_date > now().date():
            return first_pending_lesson.date.weekday()
        return None

    def restore_old_tutor_availability(self, tutor, day, lesson_start_time, duration):

        try:
            start_datetime = datetime.datetime.strptime(str(lesson_start_time), "%H:%M:%S")

            #print(start_datetime)
            end_time = (start_datetime + duration).time()

            #print(end_time)
        except Exception as e:
            print(f"An error occurred: {str(e)}")

        existing_availabilities = TutorAvailability.objects.filter(
            tutor=tutor,
            day=day.weekday(),
            status='Available'
        ).order_by('start_time')

        TutorAvailability.objects.filter(
            tutor=tutor,
            day=day.weekday(),
            start_time=start_datetime.time(),
            end_time=end_time
        ).update(status='Available')

        all_availabilities = TutorAvailability.objects.filter(
            tutor=tutor,
            day=day.weekday(),
            status='Available'
        ).order_by('start_time')

        self.merge_overlapping_availabilities(all_availabilities)

    def merge_overlapping_availabilities(self, availabilities):
        merged_availabilities = []
        current_slot = None

        for availability in availabilities:
            if current_slot is None:
                current_slot = availability
            elif availability.start_time <= current_slot.end_time:
                current_slot.end_time = max(current_slot.end_time, availability.end_time)
                current_slot.save()
                availability.delete()
            else:
                merged_availabilities.append(current_slot)
                current_slot = availability

        if current_slot:
            merged_availabilities.append(current_slot)

    def update_new_tutor_availability(self, new_start_time, new_day, duration, new_tutor):
        start_datetime = datetime.datetime.strptime(new_start_time, "%H:%M")
        end_time = (start_datetime + duration).time()

        availability = TutorAvailability.objects.filter(
            tutor=Tutor.objects.get(pk=new_tutor),
            day=new_day.weekday(),
            start_time__lte=start_datetime.time(),
            end_time__gte=end_time,
            status='Available'
        ).first()

        if not availability:
            raise ValueError("No matching availability found.")

        # Adjust existing slots for the new booking
        leftover_slots = []
        if availability.start_time < start_datetime.time():
            leftover_slots.append(TutorAvailability(
                tutor=availability.tutor,
                day=availability.day,
                start_time=availability.start_time,
                end_time=start_datetime.time(),
                status='Available'
            ))
        if availability.end_time > end_time:
            leftover_slots.append(TutorAvailability(
                tutor=availability.tutor,
                day=availability.day,
                start_time=end_time,
                end_time=availability.end_time,
                status='Available'
            ))

        TutorAvailability.objects.bulk_create(leftover_slots)
        availability.status = 'Unavailable'
        availability.start_time = start_datetime.time()
        availability.end_time = end_time
        availability.save()

    def update_lesson_statuses(self, old_lesson_date, next_lesson_date, time, frequency, end_date, lesson_id):
        current_date = next_lesson_date

        LessonStatus.objects.filter(
            lesson_id=Lesson.objects.get(pk=lesson_id),
            date__gte=old_lesson_date
        ).delete()

        while current_date < end_date:
            LessonStatus.objects.create(
                lesson_id=Lesson.objects.get(pk=lesson_id),
                date=current_date,
                time=time,
                status=Status.BOOKED
            )

            if frequency == 'W':
                current_date += datetime.timedelta(weeks=1)
            elif frequency == 'M':
                current_date += datetime.timedelta(weeks=4)
            else:
                raise ValueError("Frequency should be 'W' (week) or 'M' (month).")
