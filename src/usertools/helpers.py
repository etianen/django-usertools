"""Helpers used by django-usertools."""


def get_display_name(user, fallback=u"Anonymous"):
    """Returns a display name for the user."""
    return u" ".join(p for p in (user.first_name, user.last_name,) if p) or fallback