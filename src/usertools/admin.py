"""Admin classes for django-usertools."""

from __future__ import unicode_literals

from functools import partial

from django import template
from django.conf import settings
from django.conf.urls import url
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import AdminPasswordChangeForm
from django.contrib.auth.admin import UserAdmin as UserAdminBase, GroupAdmin as GroupAdminBase
from django.contrib import admin, auth
from django.contrib.admin.utils import flatten_fieldsets
from django.core.exceptions import PermissionDenied
try:
    from django.urls import reverse
except ImportError:  # Django < 1.10 pragma: no cover
    from django.core.urlresolvers import reverse
from django.core.mail import send_mail
from django.db import transaction
from django.db.models import Count
from django.shortcuts import render, redirect
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import int_to_base36, base36_to_int
from django.utils.encoding import force_text

from usertools.forms import UserCreationForm, UserChangeForm, UserInviteForm


# Mix in watson search, if available.
if "watson" in settings.INSTALLED_APPS:
    import watson
    AdminBase = watson.SearchAdmin
else:
    AdminBase = admin.ModelAdmin


class UserAdmin(UserAdminBase, AdminBase):

    """Enhanced user admin class."""

    add_form = UserCreationForm

    form = UserChangeForm

    invite_form = UserInviteForm

    invite_confirm_form = AdminPasswordChangeForm

    add_form_template = "admin/auth/user/add_form_usertools.html"

    invite_form_template = "admin/auth/user/invite_form.html"

    invite_confirm_form_template = "admin/auth/user/invite_confirm_form.html"

    search_fields = ("username", "first_name", "last_name", "email",)

    actions = ("invite_selected", "activate_selected", "deactivate_selected",)

    list_display = ("username", "first_name", "last_name", "email", "is_staff", "is_active",)

    list_filter = ("is_staff", "is_active", "groups",)

    fieldsets = (
        (None, {
            "fields": ("username", "is_staff", "is_active",),
        }),
        ("Personal information", {
            "fields": ("first_name", "last_name", "email",),
        }),
        ("Permissions", {
            "fields": ("is_superuser", "groups",),
        }),
        ("Advanced permissions", {
            "fields": ("user_permissions",),
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
        ("Permissions", {
            "fields": ("is_superuser", "groups",),
        }),
        ("Advanced permissions", {
            "fields": ("user_permissions",),
            "classes": ("collapse",),
        }),
    )

    invite_fieldsets = (
        (None, {
            "fields": ("username",),
        }),
        ("Personal information", {
            "fields": ("first_name", "last_name", "email",),
        }),
        ("Permissions", {
            "fields": ("is_superuser", "groups",),
        }),
        ("Advanced permissions", {
            "fields": ("user_permissions",),
            "classes": ("collapse",),
        }),
    )

    invite_confirm_fieldsets = (
        (None, {
            "fields": ("password1", "password2"),
        }),
    )

    filter_horizontal = ("groups", "user_permissions",)

    # Custom actions.

    def do_send_invitation_email(self, request, user):
        """Sends an invitation email to the given user."""
        confirmation_url = request.build_absolute_uri(
            reverse("{admin_site}:auth_user_invite_confirm".format(
                admin_site=self.admin_site.name,
            ), kwargs={
                "uidb36": int_to_base36(user.id),
                "token": default_token_generator.make_token(user),
            })
        )
        send_mail(
            "{prefix}You have been invited to create an account".format(
                prefix=settings.EMAIL_SUBJECT_PREFIX,
            ),
            template.loader.render_to_string("admin/auth/user/invite_email.txt", {
                "user": user,
                "confirmation_url": confirmation_url,
                "sender": request.user,
            }),
            settings.DEFAULT_FROM_EMAIL,
            ("{first_name} {last_name} <{email}>".format(
                first_name=user.first_name,
                last_name=user.last_name,
                email=user.email,
            ),),
        )

    def invite_selected(self, request, qs):
        """Sends an invitation email to the selected users."""
        count = 0
        for user in qs.iterator():
            self.do_send_invitation_email(request, user)
            count += 1
        self.message_user(request, "{count} {item} sent an invitation email.".format(
            count=count,
            item=count != 1 and "users were" or "user was",
        ))
    invite_selected.short_description = "Invite selected users to the admin system"

    def activate_selected(self, request, qs):
        """Activates the selected users."""
        qs.update(is_active=True)
        count = qs.count()
        self.message_user(request, "{count} {item} marked as active.".format(
            count=count,
            item=count != 1 and "users were" or "user was",
        ))
    activate_selected.short_description = "Mark selected users as active"

    def deactivate_selected(self, request, qs):
        """Deactivates the selected users."""
        qs.update(is_active=False)
        count = qs.count()
        self.message_user(request, "{count} {item} marked as inactive.".format(
            count=count,
            item=count != 1 and "users were" or "user was",
        ))
    deactivate_selected.short_description = "Mark selected users as inactive"

    def add_selected_to_group(self, request, qs, group):
        """Adds the selected users to a group."""
        for user in qs:
            user.groups.add(group)
        count = len(qs)
        self.message_user(request, "{count} {item} added to {group}.".format(
            count=count,
            item=count != 1 and "users were" or "user was",
            group=group,
        ))

    def remove_selected_from_group(self, request, qs, group):
        """Removes the selected users from a group."""
        for user in qs:
            user.groups.remove(group)
        count = len(qs)
        self.message_user(request, "{count} {item} removed from {group}.".format(
            count=count,
            item=count != 1 and "users were" or "user was",
            group=group,
        ))

    def get_actions(self, request):
        """Returns the actions this admin class supports."""
        actions = super(UserAdmin, self).get_actions(request)
        # Add in the group actions.
        groups = [
            ("{slug}_{pk}".format(
                slug=force_text(group).replace(" ", "_").lower(),
                pk=group.pk,
            ), group)
            for group
            in Group.objects.all()
        ]
        # Create the add actions.
        for group_slug, group in groups:
            add_action_name = "add_selected_to_{group_slug}".format(
                group_slug=group_slug,
            )
            actions[add_action_name] = (
                partial(self.__class__.add_selected_to_group, group=group),
                add_action_name,
                "Add selected users to {group}".format(
                    group=group,
                ),
            )
        # Create the remove actions.
        for group_slug, group in groups:
            remove_action_name = "remove_selected_from_{group_slug}".format(
                group_slug=group_slug,
            )
            actions[remove_action_name] = (
                partial(self.__class__.remove_selected_from_group, group=group),
                remove_action_name,
                "Remove selected users from {group}".format(
                    group=group,
                ),
            )
        # All done!
        return actions

    # Custom views.

    def get_urls(self):
        """Returns the URLs used by this admin class."""
        urlpatterns = super(UserAdmin, self).get_urls()
        admin_site = self.admin_site
        admin_view = admin_site.admin_view
        urlpatterns = [
            # User invite.
            url("^invite/$", admin_view(self.invite_user), name="auth_user_invite"),
            url(
                "^invite/(?P<uidb36>[^-]+)-(?P<token>[^/]+)/$",
                self.invite_user_confirm, name="auth_user_invite_confirm",
            ),
        ] + urlpatterns
        return urlpatterns

    @transaction.atomic()
    def invite_user(self, request):
        """Sends an invitation email with a login token."""
        # Check for add and change permission.
        has_add_permission = self.has_add_permission(request)
        has_change_permission = self.has_change_permission(request)
        try:
            has_view_permission = self.has_view_permission(request)
        except AttributeError:
            has_view_permission = True
        if not has_add_permission or not has_change_permission:
            raise PermissionDenied
        # Process the form.
        InviteForm = self.get_form(
            request,
            form=self.invite_form,
            fields=flatten_fieldsets(self.invite_fieldsets),
        )
        if request.method == "POST":
            form = InviteForm(request.POST)
            if form.is_valid():
                # Save the user, marked as inactive.
                user = form.save(commit=False)
                user.is_active = False
                user.is_staff = True
                user.save()
                form.save_m2m()
                # Send an invitation email.
                self.do_send_invitation_email(request, user)
                # Message the user.
                self.message_user(request, "An invitation email has been sent to {email}.".format(
                    email=user.email,
                ))
                # Redirect as appropriate.
                # Using the superclass to avoid the built in munging of the add response.
                return super(UserAdminBase, self).response_add(request, user)
        else:
            form = InviteForm()
        # Create the admin form.
        admin_form = admin.helpers.AdminForm(form, self.invite_fieldsets, {})
        # Render the template.
        media = self.media + admin_form.media
        return render(request, self.invite_form_template, dict(
            self.admin_site.each_context(request),
            title="Invite user",
            opts=self.model._meta,
            form=form,
            adminform=admin_form,
            media=media,
            add=True,
            change=False,
            is_popup=False,
            save_as=self.save_as,
            has_add_permission=has_add_permission,
            has_change_permission=has_change_permission,
            has_delete_permission=self.has_delete_permission(request),
            show_delete=False,
            has_view_permission=has_view_permission,
            has_editable_inline_admin_formsets=True,
        ))

    def invite_user_confirm(self, request, uidb36, token):
        """Performs confirmation of the invite user email."""
        form = None
        admin_form = None
        # Get the user.
        try:
            uid_int = base36_to_int(uidb36)
            user = User.objects.get(id=uid_int)
        except (ValueError, User.DoesNotExist):
            valid_link = False
            user = None
        else:
            # Check the token.
            valid_link = default_token_generator.check_token(user, token)
            # Activate the account.
            if valid_link:
                # Process the form.
                if request.method == "POST":
                    form = self.invite_confirm_form(user, request.POST)
                    if form.is_valid():
                        user = form.save(commit=False)
                        # Activate the user.
                        user.is_active = True
                        user.save()
                        # Login the user.
                        user = auth.authenticate(username=user.username, password=form.cleaned_data["password1"])
                        auth.login(request, user)
                        # Message and redirect.
                        self.message_user(
                            request,
                            "Thanks for signing up! We've saved your password and logged you in.",
                        )
                        return redirect("{admin_site}:index".format(
                            admin_site=self.admin_site.name,
                        ))
                else:
                    form = self.invite_confirm_form(user)
                admin_form = admin.helpers.AdminForm(form, self.invite_confirm_fieldsets, {})
        # Render the template.
        if valid_link:
            title = "Welcome to the site!"
        else:
            title = "This link has expired"
        return render(request, self.invite_confirm_form_template, dict(
            self.admin_site.each_context(request),
            title=title,
            opts=self.model._meta,
            valid_link=valid_link,
            form=form,
            adminform=admin_form,
            user=user,
        ))


# Automatcally re-register the User model with the enhanced admin class.
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


class GroupAdmin(GroupAdminBase, AdminBase):

    """Enhanced group admin class."""

    list_display = ("name", "get_user_count",)

    def get_queryset(self, request, *args, **kwargs):
        """Modifies the queryset."""
        qs = super(GroupAdmin, self).get_queryset(request, *args, **kwargs)
        qs = qs.annotate(
            user_count=Count("user"),
        )
        return qs

    def get_user_count(self, obj):
        """Returns the number of users in the given group."""
        return obj.user_count
    get_user_count.short_description = "members"


# Automatcally re-register the Group model with the enhanced admin class.
admin.site.unregister(Group)
admin.site.register(Group, GroupAdmin)
