# world/professions.py
"""
Profession definitions for the Space MUD.

Each profession is an operational specialization that shapes stat growth
on level-up and determines which advanced skills the unit can learn.
Requires chassis installed and level >= 3 to select.

To add or modify professions, edit the PROFESSIONS dict below.
"""

PROFESSIONS = {
    "combat_protocol": {
        "name": "Combat Protocol",
        "description": "Optimised for engagement. High processing growth.",
        "growth": {
            "max_integrity": 5,
            "processing": 2,
            "shielding": 1,
            "max_power": 3,
        },
        "skills": {
            3: "upload_virus",
            5: "overclock",
        },
    },
    "systems_engineer": {
        "name": "Systems Engineer",
        "description": "Optimised for repair and maintenance. High repair level growth.",
        "growth": {
            "max_integrity": 8,
            "processing": 1,
            "shielding": 1,
            "repair_level": 1,
            "max_power": 5,
        },
        "skills": {
            3: "emergency_patch",
            5: "diagnostic_scan",
        },
    },
    "infiltration_protocol": {
        "name": "Infiltration Protocol",
        "description": "Optimised for stealth and hacking. Balanced growth.",
        "growth": {
            "max_integrity": 5,
            "processing": 1,
            "shielding": 1,
            "max_power": 8,
        },
        "skills": {
            3: "hack_console",
            5: "stealth_mode",
        },
    },
    "broadcast_protocol": {
        "name": "Broadcast Protocol",
        "description": "Optimised for support and communication.",
        "growth": {
            "max_integrity": 7,
            "processing": 1,
            "shielding": 1,
            "max_power": 6,
        },
        "skills": {
            3: "signal_boost",
            5: "power_surge",
        },
    },
}
