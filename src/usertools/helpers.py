"""Helpers used by django-usertools."""


def get_display_name(user, fallback=None):
    """Returns a display name for the user."""
    fallback = fallback or u"Anonymous"
    return u" ".join(p for p in (user.first_name, user.last_name,) if p) or fallback