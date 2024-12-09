from datetime import timedelta
from django import template

register = template.Library()

@register.filter
def format_duration(value):
    """Format timedelta value as hours and minutes"""
    if isinstance(value, timedelta):
        hours, remainder = divmod(value.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        return f"{hours}h {minutes}min"
    return value

@register.filter
def format_frequency(value):
    """Format frequency value ('W', 'M', 'D') as ('Week', 'Month' and 'Day'))"""
    if value == 'W':
        return 'Week'
    elif value == 'M':
        return 'Month'
    elif value == 'D':
        return 'Day'
    return value

@register.filter
def format_day(value):
    """Format frequency value ('W', 'M', 'D') as ('Week', 'Month' and 'Day'))"""
    if value == 'Tue':
        return 'Tuest'
    elif value == 'M':
        return 'Month'
    elif value == 'D':
        return 'Day'
    return value

@register.filter
def get(dictionary: dict, key):
    return dictionary.get(key)

@register.filter
def dict_get(dictionary, key):
    try:
        return dictionary.get(key)
    except AttributeError:
        return None

from collections import defaultdict


@register.filter
def group_by_day(tutor_availability_list):
    grouped = defaultdict(list)
    for tutor in tutor_availability_list:
        grouped[tutor.day].append(tutor)
    return grouped