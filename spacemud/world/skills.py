# world/skills.py
"""
Skill definitions for the Space MUD.

Each skill has a power cost, cooldown (seconds), and an instant effect.
Skills are either generic (available to all units) or profession-locked
(unlocked via profession at specific levels).

Effect types:
  direct_damage  — deal effect_value damage to current combat target
  heal           — restore effect_value integrity to self (capped at max)
  bonus_damage   — add effect_value to next attack's damage
  reveal_stats   — display target hostile's integrity, processing, shielding
  restore_power  — restore effect_value power to self (capped at max)
  noop           — no mechanical effect (placeholder for future)

To add or modify skills, edit the SKILLS dict below.
"""

SKILLS = {
    # Generic skills — available to all units
    "quick_scan": {
        "name": "Quick Scan",
        "description": "Scan target for weaknesses. Next attack deals +5 damage.",
        "power_cost": 10,
        "cooldown": 30,
        "effect": "bonus_damage",
        "effect_value": 5,
        "generic": True,
    },
    "emergency_reboot": {
        "name": "Emergency Reboot",
        "description": "Restore 20 integrity. Usable out of combat only.",
        "power_cost": 15,
        "cooldown": 60,
        "effect": "heal",
        "effect_value": 20,
        "generic": True,
    },
    # Combat Protocol skills
    "upload_virus": {
        "name": "Upload Virus",
        "description": "Deal 15 damage to target hostile.",
        "power_cost": 12,
        "cooldown": 20,
        "effect": "direct_damage",
        "effect_value": 15,
        "generic": False,
    },
    "overclock": {
        "name": "Overclock",
        "description": "Boost processing by 5 for next attack.",
        "power_cost": 10,
        "cooldown": 25,
        "effect": "bonus_damage",
        "effect_value": 5,
        "generic": False,
    },
    # Systems Engineer skills
    "emergency_patch": {
        "name": "Emergency Patch",
        "description": "Restore 30 integrity.",
        "power_cost": 15,
        "cooldown": 30,
        "effect": "heal",
        "effect_value": 30,
        "generic": False,
    },
    "diagnostic_scan": {
        "name": "Diagnostic Scan",
        "description": "Reveal target hostile's integrity and stats.",
        "power_cost": 5,
        "cooldown": 15,
        "effect": "reveal_stats",
        "effect_value": 0,
        "generic": False,
    },
    # Infiltration Protocol skills
    "hack_console": {
        "name": "Hack Console",
        "description": "Deal 10 damage to target hostile.",
        "power_cost": 10,
        "cooldown": 20,
        "effect": "direct_damage",
        "effect_value": 10,
        "generic": False,
    },
    "stealth_mode": {
        "name": "Stealth Mode",
        "description": "No effect yet. Placeholder for future stealth mechanic.",
        "power_cost": 10,
        "cooldown": 30,
        "effect": "noop",
        "effect_value": 0,
        "generic": False,
    },
    # Broadcast Protocol skills
    "signal_boost": {
        "name": "Signal Boost",
        "description": "Restore 10 power to self.",
        "power_cost": 0,
        "cooldown": 45,
        "effect": "restore_power",
        "effect_value": 10,
        "generic": False,
    },
    "power_surge": {
        "name": "Power Surge",
        "description": "Deal 20 damage to target hostile. Costs 20 power.",
        "power_cost": 20,
        "cooldown": 40,
        "effect": "direct_damage",
        "effect_value": 20,
        "generic": False,
    },
}
