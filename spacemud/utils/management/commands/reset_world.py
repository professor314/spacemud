"""
Django management command: reset_world

Run via:  evennia reset_world --confirm
     or:  python manage.py reset_world --confirm

Deletes all world objects (rooms, exits, NPCs, hostiles, artifacts,
repairable objects) and reloads from JSON data files. Player accounts
and characters are preserved.

Requirements: 21.1, 21.2, 21.3, 21.4, 21.5
"""

import sys

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Delete all world objects and reload from JSON data files"

    def add_arguments(self, parser):
        parser.add_argument(
            "--confirm",
            action="store_true",
            help="Required flag to confirm this destructive operation",
        )

    def handle(self, *args, **options):
        if not options["confirm"]:
            self.stderr.write(
                "This will DELETE all rooms, exits, NPCs, hostiles, artifacts, "
                "and repairable objects.\n"
                "Player accounts and characters are preserved.\n"
                "Run with --confirm to proceed."
            )
            sys.exit(1)

        import evennia
        try:
            evennia._init()
        except Exception:
            pass

        self.stdout.write("Deleting world objects...")

        deleted_count = 0

        # Delete all world objects by typeclass (not player characters or accounts)
        typeclasses_to_delete = [
            "typeclasses.objects.RepairableObject",
            "typeclasses.objects.Hostile",
            "typeclasses.objects.NPC",
            "typeclasses.objects.Equipment",
            "typeclasses.objects.Artifact",
        ]
        for tc in typeclasses_to_delete:
            for obj in evennia.search_object(typeclass=tc):
                obj.delete()
                deleted_count += 1

        # Delete exits
        for obj in evennia.search_object(typeclass="evennia.objects.objects.DefaultExit"):
            obj.delete()
            deleted_count += 1

        # Delete rooms (after exits, since exits reference rooms)
        for obj in evennia.search_object(typeclass="typeclasses.rooms.StationRoom"):
            obj.delete()
            deleted_count += 1

        self.stdout.write(f"Deleted {deleted_count} world objects.")

        # Reload from JSON data files
        self.stdout.write("Loading world from JSON data files...")
        from world.loader import load_world
        load_world()

        self.stdout.write(self.style.SUCCESS("World reset complete."))
