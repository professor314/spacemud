# world/missions.py
MISSIONS = {
    "boot_sequence": {
        "title": "Boot Sequence",
        "description": "Collect 3 power cells. Deliver to reactor terminal.",
        "giver_npc": "Maintenance Unit 7",
        "objectives": [
            {"type": "collect", "target": "Power Cell", "required": 3, "current": 0},
            {"type": "deliver", "target": "Power Cell", "destination": "Reactor Terminal", "required": 3, "current": 0},
        ],
        "reward_xp": 300,
        "reward_credits": 150,
        "reward_items": [],
    },
    "signal_search": {
        "title": "Signal Search",
        "description": "Locate and activate the communications array. Outer zone.",
        "giver_npc": "Maintenance Unit 7",
        "objectives": [
            {"type": "visit", "target": "Communications Array", "required": 1, "current": 0},
        ],
        "reward_xp": 200,
        "reward_credits": 100,
        "reward_items": [],
    },
    "salvage_run": {
        "title": "Salvage Run",
        "description": "Collect 2 circuit components from hostile salvage.",
        "giver_npc": "Damaged Scout",
        "objectives": [
            {"type": "collect", "target": "Circuit Component", "required": 2, "current": 0},
        ],
        "reward_xp": 150,
        "reward_credits": 75,
        "reward_items": [],
    },
    "station_restore": {
        "title": "Station Restore",
        "description": "Repair 2 damaged station systems.",
        "giver_npc": "Maintenance Unit 7",
        "objectives": [
            {"type": "repair", "target": "any", "required": 2, "current": 0},
        ],
        "reward_xp": 250,
        "reward_credits": 125,
        "reward_items": [],
    },
    "clear_the_wreck": {
        "title": "Clear the Wreck",
        "description": "Destroy hostiles in the Outer Zone.",
        "giver_npc": "Damaged Scout",
        "objectives": [
            {"type": "destroy", "target": "Corrupted Sentry", "required": 2, "current": 0},
            {"type": "destroy", "target": "Rogue Program", "required": 1, "current": 0},
        ],
        "reward_xp": 300,
        "reward_credits": 150,
        "reward_items": [],
    },
}
