"""Admin classes for django-usertools."""

from django.conf import settings
from django.conf.urls.defaults import url, patterns
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin as UserAdminBase, GroupAdmin as GroupAdminBase
from django.contrib import admin
from django.contrib.admin import helpers
from django.core.exceptions import PermissionDenied
from django.db.models import Sum
from django.shortcuts import render, get_object_or_404


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
    
    list_filter = ("is_staff", "is_active", "groups",)
    
    fieldsets = (
        (None, {
            "fields": ("username", "is_staff", "is_active",),
        }),
        ("Personal information", {
            "fields": ("first_name", "last_name", "email",),
        }),
        ("Groups", {
            "fields": ("groups",),
        }),
        ("Advanced permissions", {
            "fields": ("user_permissions", "is_superuser",),
            "classes": ("collapse",),
        }),
    )
    
    filter_horizontal = ("groups", "user_permissions",)
    
    def get_urls(self):
        """Returns the URLs used by this admin class."""
        urlpatterns = super(UserAdmin, self).get_urls()
        admin_view = self.admin_site.admin_view
        urlpatterns = patterns("",
        ) + urlpatterns
        return urlpatterns
    

# Automatcally re-register the User model with the enhanced admin class.    
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


class GroupAdmin(GroupAdminBase, AdminBase):

    """Enhanced group admin class."""
    
    list_display= ("name", "get_user_count",)
    
    def queryset(self, request):
        """Modifies the queryset."""
        qs = super(GroupAdmin, self).queryset(request)
        qs = qs.annotate(
            user_count = Sum("user"),
        )
        return qs
        
    def get_user_count(self, obj):
        """Returns the number of users in the given group."""
        return obj.user_count or 0
    get_user_count.short_description = "members"
    
    
# Automatcally re-register the Group model with the enhanced admin class.    
admin.site.unregister(Group)
admin.site.register(Group, GroupAdmin)