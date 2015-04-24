"""Forms used by django-usertools."""

from django import forms
from django.contrib.auth.forms import UserCreationForm as UserCreationFormBase, UserChangeForm as UserChangeFormBase, AuthenticationForm
from django.contrib.auth.models import User, Group
from django.contrib.admin.widgets import FilteredSelectMultiple, AdminTextInputWidget
from django.utils.text import capfirst

from usertools.models import patch_username_field


def get_default_groups():
    """Returns the default groups for a user."""
    return Group.objects.filter(name="Administrators")


class UserCreationForm(UserCreationFormBase):

    """The form used by the admin site to create a user."""

    is_staff = forms.BooleanField(
        label = User._meta.get_field("is_staff").verbose_name,
        initial = True,
        required = False,
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
        fields = ("username", "is_staff", "first_name", "last_name", "email", "groups", "user_permissions", "is_superuser",)


if "username" in UserCreationForm.base_fields:
    patch_username_field(UserCreationForm.base_fields["username"])
        
        
class UserInviteForm(forms.ModelForm):

    """Form to allow users to be invited into the system, and choose their own passwords."""
    
    # These fields are required for the invitation email.
    
    first_name = forms.CharField(
        label = capfirst(User._meta.get_field("first_name").verbose_name),
        required = True,
        help_text = User._meta.get_field("first_name").help_text,
        widget = AdminTextInputWidget,
    )
    
    last_name = forms.CharField(
        label = capfirst(User._meta.get_field("last_name").verbose_name),
        required = True,
        help_text = User._meta.get_field("last_name").help_text,
        widget = AdminTextInputWidget,
    )
    
    email = forms.EmailField(
        required = True,
        help_text = User._meta.get_field("email").help_text,
        widget = AdminTextInputWidget,
    )
    
    # Set the default groups.
    
    groups = forms.ModelMultipleChoiceField(
        required = False,
        queryset = Group.objects.all(),
        widget = FilteredSelectMultiple("groups", False),
        initial = get_default_groups,
        help_text = User._meta.get_field("groups").help_text,
    )

    class Meta:
        fields = ("username", "first_name", "last_name", "email", "groups", "user_permissions", "is_superuser",)
        model = User
        
        
class UserChangeForm(UserChangeFormBase):
    
    """A customized user change form."""
    
    def clean_password(self):
        # HACK: Needed to prevent crash when saving user.
        return self.initial.get("password", "")
    
    
patch_username_field(UserChangeForm.base_fields["username"])


patch_username_field(AuthenticationForm.base_fields["username"])