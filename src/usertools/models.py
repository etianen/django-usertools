"""Models used by django-usertools."""

from django.conf import settings
from django.contrib.auth.models import User
from django.core.validators import MaxLengthValidator
from django.utils.encoding import force_text


ORIGINAL_USERNAME_MAX_LENGTH = USERNAME_MAX_LENGTH = User._meta.get_field("username").max_length


def patch_username_field(field):
    """Dummy implementation of patching a username field."""
    pass


# If south is installed, and the migrations are installed, we can safely increase the username max length.
if "south" in settings.INSTALLED_APPS and getattr(settings, "SOUTH_MIGRATION_MODULES", {}).get("auth") == "usertools.migrations_auth":
    USERNAME_MAX_LENGTH = 75
    def patch_username_field(field):
        """Patches the given username field to use the new max_length setting."""
        for validator in field.validators:
            if isinstance(validator, MaxLengthValidator):
                validator.limit_value = USERNAME_MAX_LENGTH
        field.max_length = USERNAME_MAX_LENGTH
        field.help_text = field.help_text.replace(force_text(ORIGINAL_USERNAME_MAX_LENGTH), force_text(USERNAME_MAX_LENGTH))
        if hasattr(field, "widget"):
            field.widget.attrs["maxlength"] = USERNAME_MAX_LENGTH
    patch_username_field(User._meta.get_field("username"))