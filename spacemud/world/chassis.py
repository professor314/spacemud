# world/chassis.py
"""
Chassis definitions for the Space MUD.

Each chassis is a robot body type that the player selects permanently
at a Chassis Terminal. Chassis provide stat modifiers and a passive ability.

To add or modify chassis types, edit the CHASSIS dict below.
"""

CHASSIS = {
    "scout": {
        "name": "Scout Unit",
        "description": "Lightweight frame. High processing, low shielding.",
        "stat_modifiers": {"processing": 3, "shielding": -1, "max_power": 10},
        "passive": "enhanced_sensors",
        "passive_description": "Sensor range extended. Room scan shows exits of adjacent rooms.",
    },
    "heavy": {
        "name": "Heavy Unit",
        "description": "Reinforced frame. High integrity and shielding, low processing.",
        "stat_modifiers": {"max_integrity": 30, "shielding": 3, "processing": -2},
        "passive": "damage_reduction",
        "passive_description": "Physical damage reduced by 2 per hit (minimum 1).",
    },
    "repair": {
        "name": "Repair Unit",
        "description": "Maintenance frame. High repair level, moderate stats.",
        "stat_modifiers": {"repair_level": 2, "max_integrity": 10},
        "passive": "self_repair",
        "passive_description": "Regenerates 1 integrity per minute when not in combat.",
    },
    "infiltrator": {
        "name": "Infiltrator Unit",
        "description": "Stealth frame. High processing, moderate stats.",
        "stat_modifiers": {"processing": 2, "max_power": 15},
        "passive": "reduced_detection",
        "passive_description": "Hostile entities are less likely to notice you.",
    },
    "broadcast": {
        "name": "Broadcast Unit",
        "description": "Communications frame. Balanced stats.",
        "stat_modifiers": {"max_power": 10, "max_integrity": 10},
        "passive": "cross_zone_comms",
        "passive_description": "Can transmit messages to other units in any zone.",
    },
}
