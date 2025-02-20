from django import template

register = template.Library()

@register.filter
def times(number):
    return range(1, number + 1)  # Returns a list of numbers from 1 to `number`

@register.filter
def get_item(dictionary, key):
    """Gets an item from a dictionary using a key."""
    return dictionary.get(key, "")
