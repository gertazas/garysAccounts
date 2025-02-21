from django import template

register = template.Library()

@register.filter
def times(number):
    """Returns a range object for iteration in templates."""
    try:
        return range(int(number))
    except (TypeError, ValueError):
        return []

@register.filter
def get_item(dictionary, key):
    """Gets an item from a dictionary using a key."""
    return dictionary.get(key, "")

@register.filter
def get_item_dict(dictionary, key):
    """Retrieve a dictionary item by key, safely handling non-dict values."""
    if isinstance(dictionary, dict):
        return dictionary.get(key, {})
    return {}  # Return an empty dictionary if the input is not a dictionary

@register.filter
def subtract(value, arg):
    """Subtract arg from value, handling None values."""
    try:
        return float(value) - float(arg) if value and arg else float(value or 0)
    except (TypeError, ValueError):
        return 0  # Fallback to 0 if there's an issue

@register.filter
def get_index(lst, idx):
    """Returns the element at index `idx` from list `lst`."""
    try:
        return lst[int(idx)]
    except (IndexError, ValueError, TypeError):
        return ""
