"""Creates or maintains an initial set of authentication groups."""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Permission, Group, User
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.db import transaction


class Command(BaseCommand):

    help = "Creates or maintains an initial set of authentication groups."

    @transaction.atomic()
    def handle(self, *args, **kwargs):
        """Runs the command."""
        verbosity = int(kwargs.get("verbosity"))
        # Create the administrators group.
        administrators, _ = Group.objects.get_or_create(name="Administrators")
        administrator_permissions = Permission.objects.exclude(
            Q(id__in=administrators.permissions.all()),
        )
        administrators.permissions.add(*administrator_permissions)
        if verbosity >= 2:
            self.stdout.write("Synced administrators group.\n")
        # Create the editor group.
        editors, _ = Group.objects.get_or_create(name="Editors")
        editor_permissions = Permission.objects.exclude(
            Q(content_type__in=(ContentType.objects.get_for_model(Group), ContentType.objects.get_for_model(User),)) |
            Q(id__in=editors.permissions.all()),
        )
        editors.permissions.add(*editor_permissions)
        if verbosity >= 2:
            self.stdout.write("Synced editors group.\n")
