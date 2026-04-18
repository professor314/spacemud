"""
Django management command: validate_world

Run via:  evennia validate_world

Checks world data integrity for the Space MUD and reports any errors.
Exits with status code 1 if errors are found, 0 if the world is clean.
"""

import sys

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Validate world data integrity for the Space MUD"

    def handle(self, *args, **options):
        from utils.validate_world import validate_world

        self.stdout.write("Running world validation checks...")

        errors = validate_world()

        if errors:
            for error in errors:
                self.stderr.write(self.style.ERROR(f"ERROR: {error}"))
            self.stderr.write(
                self.style.ERROR(f"\n{len(errors)} error(s) found.")
            )
            sys.exit(1)
        else:
            self.stdout.write(
                self.style.SUCCESS("World validation passed. No errors found.")
            )
            sys.exit(0)
