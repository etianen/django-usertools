"""Admin classes for django-usertools."""

from functools import partial

from django.conf import settings
from django.conf.urls.defaults import url, patterns
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin as UserAdminBase, GroupAdmin as GroupAdminBase
from django.contrib import admin
from django.db.models import Count

from usertools.forms import UserCreationForm


# Mix in watson search, if available.
if "watson" in settings.INSTALLED_APPS:
    import watson
    AdminBase = watson.SearchAdmin
else:
    AdminBase = admin.ModelAdmin


class UserAdmin(UserAdminBase, AdminBase):

    """Enhanced user admin class."""
    
    add_form = UserCreationForm
    
    add_form_template = "admin/auth/user/add_form_usertools.html"
    
    search_fields = ("username", "first_name", "last_name", "email",)
    
    actions = ("activate_selected", "deactivate_selected",)
    
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
    
    add_fieldsets = (
        (None, {
            "fields": ("username", "is_staff",),
        }),
        ("Password", {
            "fields": ("password1", "password2",),
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
    
    # Custom actions.
    
    def activate_selected(self, request, qs):
        """Activates the selected users."""
        qs.update(is_active=True)
        count = qs.count()
        self.message_user(request, u"{count} {item} marked as active.".format(
            count = count,
            item = count != 1 and "users were" or "user was",
        ))
    activate_selected.short_description = "Mark selected users as active"
    
    def deactivate_selected(self, request, qs):
        """Deactivates the selected users."""
        qs.update(is_active=False)
        count = qs.count()
        self.message_user(request, u"{count} {item} marked as inactive.".format(
            count = count,
            item = count != 1 and "users were" or "user was",
        ))
    deactivate_selected.short_description = "Mark selected users as inactive"
    
    def add_selected_to_group(self, request, qs, group):
        """Adds the selected users to a group."""
        for user in qs:
            user.groups.add(group)
        count = len(qs)
        self.message_user(request, u"{count} {item} added to {group}.".format(
            count = count,
            item = count != 1 and "users were" or "user was",
            group = group,
        ))
            
    def remove_selected_from_group(self, request, qs, group):
        """Removes the selected users from a group."""
        for user in qs:
            user.groups.remove(group)
        count = len(qs)
        self.message_user(request, u"{count} {item} removed from {group}.".format(
            count = count,
            item = count != 1 and "users were" or "user was",
            group = group,
        ))
    
    def get_actions(self, request):
        """Returns the actions this admin class supports."""
        actions = super(UserAdmin, self).get_actions(request)
        # Add in the group actions.
        groups = [
            (u"{slug}_{pk}".format(
                slug = unicode(group).replace(" ", "_").lower(),
                pk = group.pk,
            ), group)
            for group
            in Group.objects.all()
        ]
        # Create the add actions.
        for group_slug, group in groups:
            add_action_name = u"add_selected_to_{group_slug}".format(
                group_slug = group_slug,
            )
            actions[add_action_name] = (
                partial(self.__class__.add_selected_to_group, group=group),
                add_action_name,
                "Add selected users to {group}".format(
                    group = group,
                ),
            )
        # Create the remove actions.
        for group_slug, group in groups:
            remove_action_name = u"remove_selected_from_{group_slug}".format(
                group_slug = group_slug,
            )
            actions[remove_action_name] = (
                partial(self.__class__.remove_selected_from_group, group=group),
                remove_action_name,
                "Remove selected users from {group}".format(
                    group = group,
                ),
            )
        # All done!
        return actions
    
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
            user_count = Count("user"),
        )
        return qs
        
    def get_user_count(self, obj):
        """Returns the number of users in the given group."""
        return obj.user_count
    get_user_count.short_description = "members"
    
    
# Automatcally re-register the Group model with the enhanced admin class.    
admin.site.unregister(Group)
admin.site.register(Group, GroupAdmin)