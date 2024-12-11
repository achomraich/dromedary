from django.test import TestCase
from django.urls import reverse
from datetime import datetime, timedelta, date
from random import choice
from tutorials.models.models import User, Admin, Student, Tutor, Lesson, LessonStatus, Subject, Term

class StudentsTestCase(TestCase):

    fixtures = [
        'tutorials/tests/fixtures/default_user.json',
        'tutorials/tests/fixtures/other_users.json',
        'tutorials/tests/fixtures/default_tutor.json',
        'tutorials/tests/fixtures/default_student.json',
        'tutorials/tests/fixtures/default_lesson.json',
        'tutorials/tests/fixtures/default_subject.json',
        'tutorials/tests/fixtures/default_term.json',
        'tutorials/tests/fixtures/default_lesson_status.json',
    ]

    def setUp(self):
        self.admin_user = User.objects.get(username='@johndoe')
        self.admin = Admin.objects.create(user=self.admin_user)

        self.tutor = Tutor.objects.get(user__username='@petrapickles')

        self.student = Student.objects.get(user__username='@janedoe')

        
        self.year = 2024
        self.month = 12
        self.term = Term.objects.create(
            start_date=date(self.year, self.month, 1),
            end_date=date(self.year, self.month, 31)
        )
        subject = Subject.objects.create(pk=3, name='Python')
        self.lesson = Lesson.objects.create(
            tutor=self.tutor,
            student=self.student,
            subject=subject,
            start_date=date(self.year, self.month, 4),
            frequency='W',
            duration=timedelta(minutes=60),
            price_per_lesson=50.00,
            term=self.term
        )
        self.lesson_status = LessonStatus.objects.filter(lesson_id=self.lesson)


    def test_student_calendar_access(self):
        self.client.login(username='@janedoe', password='Password123')
        response = self.client.get(reverse('calendar', kwargs={'year': self.year, 'month': self.month}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shared/calendar.html')
        self.assertContains(response, self.student.user.username)
        self.assertContains(response, self.tutor.user.username)
        self.assertContains(response, self.lesson.subject)
        self.assertContains(response, 'Dec. 4, 2024')
        self.assertContains(response, 'Dec. 11, 2024')
        self.assertContains(response, 'Dec. 18, 2024')
        self.assertContains(response, 'Dec. 25, 2024')
        self.assertContains(response, self.lesson_status[0].status)

    
    def test_no_lessons_for_empty_calendar(self):
        self.client.login(username='@janedoe', password='Password123')
        response = self.client.get(reverse('calendar', kwargs={'year': self.year, 'month': self.month-1}))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shared/calendar.html')
        self.assertContains(response, "No lessons during this week")
    
    def test_calendar_navigation_next_month(self):
        self.client.login(username='@janedoe', password='Password123')
        next_month_url = reverse('calendar', kwargs={'year': 2024, 'month': 1})
        response = self.client.get(next_month_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shared/calendar.html')
        self.assertContains(response, 'January 2024')

    def test_calendar_navigation_previous_month(self):
        self.client.login(username='@janedoe', password='Password123')
        prev_month_url = reverse('calendar', kwargs={'year': 2023, 'month': 12})
        response = self.client.get(prev_month_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shared/calendar.html')
        self.assertContains(response, 'December 2023')

    def test_tutor_calendar_access(self):
        self.client.login(username='@petrapickles', password='Password123')
        response = self.client.get(reverse('calendar', kwargs={'year': self.year, 'month': self.month}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shared/calendar.html')
        
        self.assertContains(response, self.student.user.username)
        self.assertContains(response, self.tutor.user.username)
        self.assertContains(response, self.lesson.subject.name)
        self.assertContains(response, 'Dec. 4, 2024')
        self.assertContains(response, 'Dec. 11, 2024')
        self.assertContains(response, 'Dec. 18, 2024')
        self.assertContains(response, 'Dec. 25, 2024')
        self.assertContains(response, self.lesson_status[0].status)
