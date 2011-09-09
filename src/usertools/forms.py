"""Forms used by django-usertools."""

from django import forms
from django.contrib.auth.forms import UserCreationForm as UserCreationFormBase
from django.contrib.auth.models import User, Group
from django.contrib.admin.widgets import FilteredSelectMultiple


def get_default_groups():
    """Returns the default groups for a user."""
    return Group.objects.filter(name__iexact="Administrators")


class UserCreationForm(UserCreationFormBase):

    """The form used by the admin site to create a user."""

    is_staff = forms.BooleanField(
        User._meta.get_field("is_staff").verbose_name,
        initial = True,
        help_text = User._meta.get_field("is_staff").help_text,
    )
    
    groups = forms.ModelMultipleChoiceField(
        required = False,
        queryset = Group.objects.all(),
        widget = FilteredSelectMultiple("groups", False),
        initial = get_default_groups,
        help_text = User._meta.get_field("groups").help_text,
    )

    class Meta:
        fields = ("username", "first_name", "last_name", "email_address", "groups", "user_permissions", "is_superuser",)