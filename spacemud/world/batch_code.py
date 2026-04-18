# world/batch_code.py
"""
Space MUD — World Content Loader

Loads all world content from JSON data files via the generic loader.
Run via Python shell:
    from world.batch_code import main
    main(caller)
"""


def main(caller):
    """
    Entry point for loading world content.

    Args:
        caller: The object that invoked the script (used for feedback messages).
    """
    from world.loader import load_world
    load_world(caller)
