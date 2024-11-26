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
def get(dictionary: dict, key):
    print(f"Type of update_message: {type(dictionary)}")
    return dictionary.get(key)
