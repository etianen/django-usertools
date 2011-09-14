"""Tests for django-usertools."""

from django.core.urlresolvers import reverse
from django.contrib.auth.models import User, Group
from django.test import TestCase


class AdminTestBase(TestCase):

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