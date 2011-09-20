"""Tests for django-usertools."""

from django.contrib import admin
from django.conf.urls.defaults import patterns, url, include
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User, Group
from django.core import mail
from django.core.management import call_command
from django.test import TestCase
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import int_to_base36


admin.autodiscover()


urlpatterns = patterns("",

    url("^admin/", include(admin.site.urls)),

)


class AdminTestBase(TestCase):

    urls = "usertools.tests"

    def setUp(self):
        # Create a user.
        self.user = User(
            username = "foo",
            is_staff = True,
            is_superuser = True,
        )
        self.user.set_password("bar")
        self.user.save()
        # Log the user in.
        self.client.login(
            username = "foo",
            password = "bar",
        )
        
        
class UserAdminTest(AdminTestBase):

    def setUp(self):
        super(UserAdminTest, self).setUp()
        self.changelist_url = reverse("admin:auth_user_changelist")

    def testActivateSelectedAction(self):
        user = User.objects.create(
            username = "baz",
            is_active = False,
        )
        # Activate the user.
        response = self.client.post(self.changelist_url, {
            "action": "activate_selected",
            "_selected_action": user.id,
        })
        self.assertRedirects(response, self.changelist_url)
        self.assertEqual(User.objects.get(id=user.id).is_active, True)
        
    def testDeactivateSelectedAction(self):
        response = self.client.post(self.changelist_url, {
            "action": "deactivate_selected",
            "_selected_action": self.user.id,
        })
        self.assertRedirects(response, self.changelist_url)
        self.assertEqual(User.objects.get(id=self.user.id).is_active, False)
        
    def testAddSelectedToGroupAction(self):
        group = Group.objects.create(
            name = "Foo group",
        )
        response = self.client.post(self.changelist_url, {
            "action": "add_selected_to_foo_group_{pk}".format(pk=group.pk),
            "_selected_action": self.user.id,
        })
        self.assertRedirects(response, self.changelist_url)
        self.assertEqual(list(User.objects.get(id=self.user.id).groups.all()), [group])
        
    def testRemoveSelectedFromGroupAction(self):
        group = Group.objects.create(
            name = "Foo group",
        )
        self.user.groups.add(group)
        self.assertEqual(list(User.objects.get(id=self.user.id).groups.all()), [group])
        response = self.client.post(self.changelist_url, {
            "action": "remove_selected_from_foo_group_{pk}".format(pk=group.pk),
            "_selected_action": self.user.id,
        })
        self.assertRedirects(response, self.changelist_url)
        self.assertEqual(list(User.objects.get(id=self.user.id).groups.all()), [])
    
    def testSendInvitationEmailAction(self):
        response = self.client.post(self.changelist_url, {
            "action": "send_invitation_email_to_selected",
            "_selected_action": self.user.id,
        })
        self.assertRedirects(response, self.changelist_url)
        self.assertEqual(len(mail.outbox), 1)
        
    def testInviteUser(self):
        # Try to render the form.
        response = self.client.get("/admin/auth/user/invite/")
        self.assertEqual(response.status_code, 200)
        # Invite a user.
        response = self.client.post("/admin/auth/user/invite/", {
            "username": "bar",
            "email": "bar@foo.com",
            "first_name": "Bar",
            "last_name": "Foo",
        })
        self.assertRedirects(response, "/admin/auth/user/")
        self.assertEqual(len(mail.outbox), 1)
        user = User.objects.get(username="bar")
        self.assertTrue(user.is_staff)
        self.assertFalse(user.is_active)
        # Log out from the admin system.
        self.client.logout()
        # Try to complete the signup.
        confirmation_url = reverse("admin:auth_user_invite_confirm", kwargs = {
            "uidb36": int_to_base36(user.id),
            "token": default_token_generator.make_token(user),
        })
        response = self.client.post(confirmation_url, {
            "password1": "password",
            "password2": "password",
        })
        self.assertRedirects(response, "/admin/")
        user = User.objects.get(username=user.username)
        self.assertTrue(user.is_active)
        # Has the link now expired?
        response = self.client.post(confirmation_url, {
            "password1": "password",
            "password2": "password",
        })
        self.assertEqual(response.status_code, 200)  # 200 status means an error message.
        
        
class GroupAdminTest(AdminTestBase):

    def testGroupChangeList(self):
        # Create a group.
        group = Group.objects.create(
            name = "Foo group",
        )
        changelist_url = reverse("admin:auth_group_changelist")
        # Check the groups is present in the change list.
        response = self.client.get(changelist_url)
        self.assertContains(response, "Foo group")
        self.assertContains(response, "<td>0</td>")
        # Add a user, and check that the member count has increased.
        self.user.groups.add(group)
        response = self.client.get(changelist_url)
        self.assertContains(response, "Foo group")
        self.assertContains(response, "<td>1</td>")
        
        
class SyncGroupsCommandTest(TestCase):

    def testSyncGroupsCommand(self):
        call_command("syncgroups")
        self.assertEqual(Group.objects.count(), 2)
        self.assertEqual(Group.objects.filter(name="Administrators").count(), 1)
        self.assertEqual(Group.objects.filter(name="Editors").count(), 1)