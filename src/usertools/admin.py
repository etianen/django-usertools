"""Admin classes for django-usertools."""

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as UserAdminBase
from django.contrib import admin


# Mix in watson search, if available.
if "watson" in settings.INSTALLED_APPS:
    import watson
    AdminBase = watson.SearchAdmin
else:
    AdminBase = admin.ModelAdmin


class UserAdmin(UserAdminBase, AdminBase):

    """Enhanced user admin class."""
    
    search_fields = ("username", "first_name", "last_name", "email",)
    
    list_display = ("username", "first_name", "last_name", "email", "is_staff", "is_active",)
    
    list_filter = ("is_staff", "is_active",)
    

# Automatcally re-register the User model with the enhanced admin class.    
admin.site.unregister(User)
admin.site.register(User, UserAdmin)