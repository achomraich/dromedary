from django.test import TestCase
from django.urls import reverse
from django.contrib.messages import get_messages, ERROR

from tutorials.models.models import TutorAvailability
from tutorials.forms import TutorAvailabilityForm


class AvailabilityTestCase(TestCase):

    fixtures = [
        'tutorials/tests/fixtures/default_user.json',
        'tutorials/tests/fixtures/other_users.json',
        'tutorials/tests/fixtures/default_tutor.json',
        'tutorials/tests/fixtures/default_student.json',
        'tutorials/tests/fixtures/default_lesson.json',
        'tutorials/tests/fixtures/default_subject.json',
        'tutorials/tests/fixtures/default_term.json',
        'tutorials/tests/fixtures/default_availability.json'
    ]

    def setUp(self):
        self.url = reverse('availability')
        self.client.login(username='@petrapickles', password='Password123')

        self.availability1 = TutorAvailability.objects.get(pk=1)
        self.availability2 = TutorAvailability.objects.get(pk=2)

    def test_availability_url(self):
        self.assertEqual(self.url,'/availability/')

    def test_get_availability_by_tutor(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tutor/my_availability/availabilities.html')
        self.assertContains(response, self.availability1.day)
        self.assertContains(response, self.availability2.day)

    def test_remove_availability(self):
        response = self.client.post(self.url, {
            'availability': [self.availability1.id],
            'remove': 'remove'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.url)
        self.assertFalse(TutorAvailability.objects.filter(day=0).exists())
        self.assertTrue(TutorAvailability.objects.filter(day=1).exists())

    def test_remove_availability_not_exist(self):
        response = self.client.post(self.url, {
            'availability': 3,
            'remove': 'remove'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.url)

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any(msg.message == "The selected availability does not exist." for msg in messages))

        self.assertEqual(messages[0].level, ERROR)

    def test_post_without_remove_key(self):
        response = self.client.post(self.url)

        self.assertEqual(TutorAvailability.objects.count(), 2)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.url)

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any(msg.message == "Invalid request." for msg in messages))
        self.assertEqual(messages[0].level, ERROR)

    def test_get_add_availability(self):
        # Test the GET request for adding new availability
        response = self.client.get(reverse('availability_add'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tutor/my_availability/add_edit_availability.html')
        self.assertIsInstance(response.context['form'], TutorAvailabilityForm)
        self.assertIsNone(response.context['pk'])

    def test_get_edit_availability(self):
        # Test the GET request for editing existing availability
        response = self.client.get(reverse('availability_edit', kwargs={'pk': self.availability1.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tutor/my_availability/add_edit_availability.html')
        self.assertIsInstance(response.context['form'], TutorAvailabilityForm)
        self.assertEqual(response.context['pk'], self.availability1.pk)

    def test_post_add_availability_valid_data(self):
        # Test adding new availability with valid data
        data = {
            'day': 2,
            'start_time': '10:00',
            'end_time': '13:00',
            'status': 'Available'
        }
        response = self.client.post(reverse('availability_add'), data)
        self.assertRedirects(response, self.url)
        self.assertEqual(TutorAvailability.objects.count(), 3)
        self.assertTrue(TutorAvailability.objects.filter(day=2).exists())

    def test_post_edit_availability_valid_data(self):
        # Test editing existing availability with valid data
        data = {
            'day': 1,
            'start_time': '13:00',
            'end_time': '16:00',
            'status': 'Available'
        }
        response = self.client.post(reverse('availability_edit', kwargs={'pk': self.availability1.pk}), data)
        self.assertRedirects(response, reverse('availability'))
        self.availability1.refresh_from_db()
        self.assertEqual(self.availability1.day, 1)

    def test_post_invalid_data(self):
        # Test submitting with invalid data
        data = {
            'day': '',
            'start_time': 'invalid time',
            'end_time': '',
        }
        response = self.client.post(reverse('availability_add'), data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tutor/my_availability/add_edit_availability.html')

        form = response.context['form']
        self.assertTrue(form.errors)

        self.assertIn('day', form.errors)
        self.assertIn('This field is required.', form.errors['day'])
        self.assertIn('start_time', form.errors)
        self.assertIn('Enter a valid time.', form.errors['start_time'])

        self.assertEqual(TutorAvailability.objects.count(), 2)
