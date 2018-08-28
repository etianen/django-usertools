"""Template tags used by django-usertools."""

from __future__ import absolute_import

from django import template

from usertools.helpers import get_display_name


register = template.Library()


@register.filter
def display_name(user, fallback=None):
    """Returns a display name for the user."""
    return get_display_name(user, fallback=fallback)
