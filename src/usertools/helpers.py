"""Helpers used by django-usertools."""

from __future__ import unicode_literals


def get_display_name(user, fallback=None):
    """Returns a display name for the user."""
    fallback = fallback or "Anonymous"
    return " ".join(p for p in (user.first_name, user.last_name,) if p) or fallback
