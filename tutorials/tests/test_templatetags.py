from django.test import TestCase
from datetime import timedelta
from django.template import Context, Template
from tutorials.templatetags.lesson_filters import format_duration, format_frequency, get, dict_get


class CustomTemplateFiltersTestCase(TestCase):

    def test_format_duration(self):
        duration = timedelta(hours=2, minutes=30)
        formatted_duration = format_duration(duration)
        self.assertEqual(formatted_duration, "2h 30min")

        duration = timedelta(minutes=45)
        formatted_duration = format_duration(duration)
        self.assertEqual(formatted_duration, "0h 45min")

        invalid_duration = "Invalid"
        self.assertEqual(format_duration(invalid_duration), invalid_duration)

    def test_format_frequency(self):
        self.assertEqual(format_frequency('W'), 'Week')
        self.assertEqual(format_frequency('M'), 'Month')
        self.assertEqual(format_frequency('D'), 'Day')

        self.assertEqual(format_frequency('X'), 'X')

    def test_get_filter(self):
        context = {'key': 'value'}

        value = get(context, 'key')
        self.assertEqual(value, 'value')

        value = get(context, 'invalid_key')
        self.assertIsNone(value)

    def test_dict_get_filter(self):
        context = {'key': 'value'}

        value = dict_get(context, 'key')
        self.assertEqual(value, 'value')

        value = dict_get(context, 'invalid_key')
        self.assertIsNone(value)

        invalid_context = "Not a dictionary"
        value = dict_get(invalid_context, 'key')
        self.assertIsNone(value)
