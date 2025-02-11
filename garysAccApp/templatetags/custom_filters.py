from django import template

register = template.Library()

@register.filter
def times(number):
    """Returns a range object for iteration in templates."""
    return range(int(number))
