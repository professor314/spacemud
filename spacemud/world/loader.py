# world/loader.py
"""
Generic JSON world loader for the Space MUD.

Reads JSON data files from world/data/ and creates Evennia objects.
Called by batch_code.py or the reset_world management command.

Requirements: 20.2, 20.5
"""

import json
import os

# Use evennia.utils.create.create_object directly to avoid Evennia 6.0
# lazy-loading issues with `from evennia import create_object`.
from evennia.utils.create import create_object

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


def load_world(caller=None):
    """
    Main entry point. Loads all world content from JSON data files.

    Calls sub-loaders in dependency order: rooms first (needed by everything
    else), then exits, artifacts, NPCs, hostiles, and repairables.

    Args:
        caller: Optional Evennia object to receive status messages.
    """
    rooms = _load_rooms()
    exits = _load_exits(rooms)
    artifacts = _load_artifacts(rooms)
    npcs = _load_npcs(rooms)
    hostiles = _load_hostiles(rooms)
    repairables = _load_repairables(rooms)

    summary = (
        "World loaded from JSON data files.\n"
        f"  Rooms: {len(rooms)}\n"
        f"  Exits: {exits}\n"
        f"  Artifacts: {artifacts}\n"
        f"  NPCs: {npcs}\n"
        f"  Hostiles: {hostiles}\n"
        f"  Repairables: {repairables}"
    )

    if caller:
        caller.msg(summary)
    else:
        print(summary)


def _load_json(filename):
    """
    Read and parse a JSON file from the world/data/ directory.

    Args:
        filename: Name of the JSON file (e.g. "rooms.json").

    Returns:
        Parsed JSON data (typically a list of dicts).

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file contains invalid JSON.
    """
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"World data file not found: {filename} (expected at {path})"
        )
    try:
        with open(path, "r") as f:
            return json.load(f)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Malformed JSON in {filename}: {exc}"
        ) from exc


def _load_rooms():
    """
    Create StationRoom objects from rooms.json.

    Returns:
        dict: Mapping of {room_key: room_object} for use by other loaders.
    """
    rooms = {}
    for data in _load_json("rooms.json"):
        key = data.get("key")
        if not key:
            raise ValueError(
                "rooms.json: entry missing required 'key' field"
            )

        room = create_object(
            "typeclasses.rooms.StationRoom",
            key=key,
            location=None,
        )
        room.db.desc = data.get("desc", "")
        room.db.zone = data.get("zone", "unknown")
        room.db.pvp_zone = data.get("pvp_zone", False)

        for tag in data.get("tags", []):
            room.tags.add(tag)

        rooms[key] = room

    return rooms


def _load_exits(rooms):
    """
    Create DefaultExit objects from exits.json.

    Args:
        rooms: dict of {room_key: room_object} from _load_rooms.

    Returns:
        int: Number of exits created.
    """
    count = 0
    for data in _load_json("exits.json"):
        from_key = data.get("from")
        to_key = data.get("to")
        direction = data.get("direction")

        if not all([from_key, to_key, direction]):
            raise ValueError(
                f"exits.json: entry missing required field(s). "
                f"Got: from={from_key!r}, to={to_key!r}, direction={direction!r}"
            )

        from_room = rooms.get(from_key)
        to_room = rooms.get(to_key)

        if not from_room:
            raise ValueError(
                f"exits.json: 'from' room {from_key!r} not found in rooms"
            )
        if not to_room:
            raise ValueError(
                f"exits.json: 'to' room {to_key!r} not found in rooms"
            )

        create_object(
            "evennia.objects.objects.DefaultExit",
            key=direction,
            location=from_room,
            destination=to_room,
        )
        count += 1

    return count


def _load_artifacts(rooms):
    """
    Create Artifact/Equipment objects from artifacts.json.

    Args:
        rooms: dict of {room_key: room_object} from _load_rooms.

    Returns:
        int: Number of artifacts created.
    """
    count = 0
    for data in _load_json("artifacts.json"):
        key = data.get("key")
        location_key = data.get("location")
        typeclass = data.get("typeclass")

        if not key:
            raise ValueError(
                "artifacts.json: entry missing required 'key' field"
            )
        if not typeclass:
            raise ValueError(
                f"artifacts.json: entry {key!r} missing required 'typeclass' field"
            )

        location = rooms.get(location_key) if location_key else None
        if location_key and not location:
            raise ValueError(
                f"artifacts.json: location {location_key!r} for artifact "
                f"{key!r} not found in rooms"
            )

        obj = create_object(
            typeclass,
            key=key,
            location=location,
        )
        obj.db.desc = data.get("desc", "")
        obj.db.item_type = data.get("item_type", "misc")
        obj.db.equippable = data.get("equippable", False)
        obj.db.stat_modifiers = data.get("stat_modifiers", {})

        count += 1

    return count


def _load_npcs(rooms):
    """
    Create NPC objects from npcs.json.

    Args:
        rooms: dict of {room_key: room_object} from _load_rooms.

    Returns:
        int: Number of NPCs created.
    """
    count = 0
    for data in _load_json("npcs.json"):
        key = data.get("key")
        location_key = data.get("location")

        if not key:
            raise ValueError(
                "npcs.json: entry missing required 'key' field"
            )

        location = rooms.get(location_key) if location_key else None
        if location_key and not location:
            raise ValueError(
                f"npcs.json: location {location_key!r} for NPC "
                f"{key!r} not found in rooms"
            )

        npc = create_object(
            "typeclasses.objects.NPC",
            key=key,
            location=location,
        )
        npc.db.desc = data.get("desc", "")
        npc.db.role = data.get("role", "ambient")
        npc.db.home_location = location
        npc.db.dialogue = data.get("dialogue", "")
        npc.db.missions_offered = data.get("missions_offered", [])

        count += 1

    return count


def _load_hostiles(rooms):
    """
    Create Hostile objects from hostiles.json.

    Args:
        rooms: dict of {room_key: room_object} from _load_rooms.

    Returns:
        int: Number of hostiles created.
    """
    count = 0
    for data in _load_json("hostiles.json"):
        key = data.get("key")
        location_key = data.get("location")

        if not key:
            raise ValueError(
                "hostiles.json: entry missing required 'key' field"
            )

        location = rooms.get(location_key) if location_key else None
        if location_key and not location:
            raise ValueError(
                f"hostiles.json: location {location_key!r} for hostile "
                f"{key!r} not found in rooms"
            )

        hostile = create_object(
            "typeclasses.objects.Hostile",
            key=key,
            location=location,
        )
        hostile.db.desc = data.get("desc", "")
        hostile.db.integrity = data.get("integrity", 50)
        hostile.db.max_integrity = data.get("max_integrity", 50)
        hostile.db.processing = data.get("processing", 8)
        hostile.db.shielding = data.get("shielding", 3)
        hostile.db.xp_reward = data.get("xp_reward", 50)
        hostile.db.credits_reward = data.get("credits_reward", 10)
        hostile.db.home_location = location
        hostile.db.respawn_delay = data.get("respawn_delay", 300)
        hostile.db.salvage_items = data.get("salvage_items", [])

        count += 1

    return count


def _load_repairables(rooms):
    """
    Create RepairableObject objects from repairables.json.

    Args:
        rooms: dict of {room_key: room_object} from _load_rooms.

    Returns:
        int: Number of repairable objects created.
    """
    count = 0
    for data in _load_json("repairables.json"):
        key = data.get("key")
        location_key = data.get("location")

        if not key:
            raise ValueError(
                "repairables.json: entry missing required 'key' field"
            )

        location = rooms.get(location_key) if location_key else None
        if location_key and not location:
            raise ValueError(
                f"repairables.json: location {location_key!r} for repairable "
                f"{key!r} not found in rooms"
            )

        obj = create_object(
            "typeclasses.objects.RepairableObject",
            key=key,
            location=location,
        )
        obj.db.repaired = False
        obj.db.repair_level_required = data.get("repair_level_required", 1)
        obj.db.repair_cost = data.get("repair_cost", {})
        obj.db.power_cost = data.get("power_cost", 0)
        obj.db.on_repair_message = data.get("on_repair_message", "")
        obj.db.requires_repaired = data.get("requires_repaired", None)
        obj.db.desc_damaged = data.get("desc_damaged", "")
        obj.db.desc_repaired = data.get("desc_repaired", "")
        # Initial description is the damaged state
        obj.db.desc = obj.db.desc_damaged

        count += 1

    return count
