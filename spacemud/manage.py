#!/usr/bin/env python
"""
Django management script for the Space MUD Evennia game.

Usage:
    python manage.py <command> [options]

This is the standard Django manage.py entry point. Evennia games use
``evennia <command>`` for most operations, but this file allows direct
Django management commands (e.g. migrate, shell, dbshell).
"""

import os
import sys


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.conf.settings")

    # Add the game directory to sys.path so that game modules are importable
    gamedir = os.path.dirname(os.path.abspath(__file__))
    if gamedir not in sys.path:
        sys.path.insert(0, gamedir)

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
