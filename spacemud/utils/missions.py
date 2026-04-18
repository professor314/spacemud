# utils/missions.py
"""
Mission system utilities.

Functions:
    show_available_missions(character, npc)  -- display missions offered by an NPC
    accept_mission(character, mission_id)    -- add mission to character's log
    try_complete_mission(character, mission_title) -- validate and complete a mission
    on_hostile_destroyed(killer, hostile, **kwargs) -- event handler for hostile death
    on_artifact_collected(character, item, **kwargs) -- event handler for artifact pickup
    _check_mission_complete(character, mission_id) -- check if all objectives are done
"""

import copy

from world.missions import MISSIONS


def show_available_missions(character, npc):
    """
    Display missions offered by *npc* that *character* has not yet started or completed.

    Shows mission title, description, and objectives for each available mission.
    """
    log = character.db.mission_log or {}
    available = []

    for mission_id in getattr(npc.db, "missions_offered", []):
        mission_def = MISSIONS.get(mission_id)
        if not mission_def:
            continue
        entry = log.get(mission_id, {})
        state = entry.get("state", "not_started")
        if state in ("in_progress", "completed"):
            continue
        available.append((mission_id, mission_def))

    if not available:
        character.msg(f"{npc.name} has no new missions for you.")
        return

    lines = [f"|w{npc.name} offers the following missions:|n"]
    for mission_id, mission_def in available:
        lines.append(f"\n  |y[{mission_id}]|n {mission_def['title']}")
        lines.append(f"  {mission_def['description']}")
        lines.append("  Objectives:")
        for obj in mission_def["objectives"]:
            if obj["type"] == "destroy":
                lines.append(
                    f"    - Destroy {obj['required']} x {obj['target']}"
                )
            elif obj["type"] == "collect":
                lines.append(
                    f"    - Collect {obj['required']} x {obj['target']}"
                )
            elif obj["type"] == "visit":
                lines.append(f"    - Visit: {obj['target']}")
            elif obj["type"] == "deliver":
                lines.append(
                    f"    - Deliver {obj['required']} x {obj['target']} to {obj.get('destination', '?')}"
                )
            else:
                lines.append(f"    - {obj['type']}: {obj['target']}")
        lines.append(
            f"  Reward: {mission_def['reward_xp']} XP, "
            f"{mission_def['reward_credits']} credits"
        )
        lines.append(f"  (Type |waccept {mission_id}|n to accept)")

    character.msg("\n".join(lines))


def accept_mission(character, mission_id):
    """
    Add *mission_id* to *character*'s mission log with state "in_progress".

    Rejects if the mission is already in progress or completed.
    Initialises objectives with current=0 using a deep copy to avoid shared state.
    """
    mission_def = MISSIONS.get(mission_id)
    if not mission_def:
        character.msg(f"Unknown mission: {mission_id}")
        return

    if character.db.mission_log is None:
        character.db.mission_log = {}

    log = character.db.mission_log
    existing = log.get(mission_id, {})
    state = existing.get("state", "not_started")

    if state == "in_progress":
        character.msg(
            f"You already have the mission '{mission_def['title']}' in progress."
        )
        return
    if state == "completed":
        character.msg(
            f"You have already completed the mission '{mission_def['title']}'."
        )
        return

    # Deep copy objectives so each character has independent progress counters
    objectives = copy.deepcopy(mission_def["objectives"])
    for obj in objectives:
        obj["current"] = 0

    log[mission_id] = {
        "state": "in_progress",
        "objectives": objectives,
    }
    # Persist the updated log
    character.db.mission_log = log

    character.msg(
        f"|gMission accepted:|n {mission_def['title']}\n"
        f"{mission_def['description']}"
    )


def try_complete_mission(character, mission_title):
    """
    Attempt to complete a mission identified by *mission_title*.

    Validates:
    - The mission exists and the character has it in progress.
    - The character is in the same room as the mission-giver NPC.
    - All objectives are complete (current >= required).

    On success: grants XP and credits, marks mission "completed", notifies character.
    """
    # Find the mission by title
    mission_id = None
    mission_def = None
    for mid, mdef in MISSIONS.items():
        if mdef["title"].lower() == mission_title.lower():
            mission_id = mid
            mission_def = mdef
            break

    if not mission_id:
        character.msg(f"No mission named '{mission_title}' found.")
        return

    log = character.db.mission_log or {}
    entry = log.get(mission_id)

    if not entry or entry.get("state") != "in_progress":
        character.msg(
            f"You don't have the mission '{mission_def['title']}' in progress."
        )
        return

    # Check that the mission-giver NPC is in the same room
    giver_name = mission_def["giver_npc"]
    giver = None
    for obj in character.location.contents:
        if obj.name == giver_name:
            giver = obj
            break

    if not giver:
        character.msg(
            f"You need to return to {giver_name} to complete this mission."
        )
        return

    # Check all objectives are complete
    objectives = entry.get("objectives", [])
    incomplete = [
        obj for obj in objectives if obj.get("current", 0) < obj.get("required", 1)
    ]
    if incomplete:
        lines = [f"Objectives incomplete for '{mission_def['title']}':"]
        for obj in incomplete:
            lines.append(
                f"  - {obj['target']}: {obj.get('current', 0)}/{obj['required']}"
            )
        character.msg("\n".join(lines))
        return

    # Grant rewards
    reward_xp = mission_def.get("reward_xp", 0)
    reward_credits = mission_def.get("reward_credits", 0)

    if reward_xp:
        character.award_xp(reward_xp)

    if reward_credits:
        character.db.credits = (character.db.credits or 0) + reward_credits

    # Mark mission completed
    entry["state"] = "completed"
    character.db.mission_log = log

    character.msg(
        f"|gMission complete:|n {mission_def['title']}\n"
        f"Rewards: |w{reward_xp}|n XP, |w{reward_credits}|n credits\n"
        f"{giver_name}: \"Task acknowledged. Compensation transferred.\""
    )


def on_hostile_destroyed(killer, hostile, **kwargs):
    """
    Event handler called when a hostile is destroyed.

    Iterates *killer*'s in-progress missions and increments matching destroy objectives
    where objective type == "destroy" and target matches hostile.name.
    Notifies character when an objective completes.
    Calls _check_mission_complete after each mission update.
    """
    if not killer or not hostile:
        return

    log = killer.db.mission_log
    if not log:
        return

    hostile_name = hostile.name

    for mission_id, entry in log.items():
        if entry.get("state") != "in_progress":
            continue

        updated = False
        for obj in entry.get("objectives", []):
            if obj.get("type") != "destroy":
                continue
            if obj.get("target") != hostile_name:
                continue
            if obj.get("current", 0) >= obj.get("required", 1):
                # Already complete — do not over-increment
                continue

            obj["current"] = obj.get("current", 0) + 1
            updated = True

            current = obj["current"]
            required = obj["required"]
            killer.msg(
                f"|yMission progress:|n {_mission_title(mission_id)} — "
                f"Destroyed {hostile_name}: {current}/{required}"
            )

            if current >= required:
                killer.msg(
                    f"|gObjective complete:|n {hostile_name} ({required}/{required})"
                )

        if updated:
            # Persist the updated log
            killer.db.mission_log = log
            _check_mission_complete(killer, mission_id)


def on_artifact_collected(character, item, **kwargs):
    """
    Event handler called when a character picks up an artifact.

    Iterates *character*'s in-progress missions and increments matching collect
    objectives where objective type == "collect" and target matches item.name.
    Notifies character when an objective completes.
    Calls _check_mission_complete after each mission update.
    """
    if not character or not item:
        return

    log = character.db.mission_log
    if not log:
        return

    item_name = item.name

    for mission_id, entry in log.items():
        if entry.get("state") != "in_progress":
            continue

        updated = False
        for obj in entry.get("objectives", []):
            if obj.get("type") != "collect":
                continue
            if obj.get("target") != item_name:
                continue
            if obj.get("current", 0) >= obj.get("required", 1):
                continue

            obj["current"] = obj.get("current", 0) + 1
            updated = True

            current = obj["current"]
            required = obj["required"]
            character.msg(
                f"|yMission progress:|n {_mission_title(mission_id)} — "
                f"Collected {item_name}: {current}/{required}"
            )

            if current >= required:
                character.msg(
                    f"|gObjective complete:|n {item_name} ({required}/{required})"
                )

        if updated:
            character.db.mission_log = log
            _check_mission_complete(character, mission_id)


def on_unit_enters_room(character, room, **kwargs):
    """
    Event handler called when a unit enters a room.

    Iterates *character*'s in-progress missions and increments matching visit
    objectives where objective type == "visit" and target matches room name.
    """
    if not character or not room:
        return

    log = character.db.mission_log
    if not log:
        return

    room_name = room.name if hasattr(room, "name") else str(room)

    for mission_id, entry in log.items():
        if entry.get("state") != "in_progress":
            continue

        updated = False
        for obj in entry.get("objectives", []):
            if obj.get("type") != "visit":
                continue
            if obj.get("target") != room_name:
                continue
            if obj.get("current", 0) >= obj.get("required", 1):
                continue

            obj["current"] = obj.get("current", 0) + 1
            updated = True

            current = obj["current"]
            required = obj["required"]
            character.msg(
                f"|yMission progress:|n {_mission_title(mission_id)} — "
                f"Visited {room_name}: {current}/{required}"
            )

            if current >= required:
                character.msg(
                    f"|gObjective complete:|n {room_name} ({required}/{required})"
                )

        if updated:
            character.db.mission_log = log
            _check_mission_complete(character, mission_id)


def on_deliver(character, item, room, **kwargs):
    """
    Event handler for deliver objectives. Called when a character drops
    an item in a room that matches a deliver objective destination.
    """
    if not character or not item or not room:
        return

    log = character.db.mission_log
    if not log:
        return

    item_name = item.name
    room_name = room.name if hasattr(room, "name") else str(room)

    for mission_id, entry in log.items():
        if entry.get("state") != "in_progress":
            continue

        updated = False
        for obj in entry.get("objectives", []):
            if obj.get("type") != "deliver":
                continue
            if obj.get("target") != item_name:
                continue
            if obj.get("destination") != room_name:
                continue
            if obj.get("current", 0) >= obj.get("required", 1):
                continue

            obj["current"] = obj.get("current", 0) + 1
            updated = True

            current = obj["current"]
            required = obj["required"]
            character.msg(
                f"|yMission progress:|n {_mission_title(mission_id)} — "
                f"Delivered {item_name}: {current}/{required}"
            )

            if current >= required:
                character.msg(
                    f"|gObjective complete:|n {item_name} delivered ({required}/{required})"
                )

        if updated:
            character.db.mission_log = log
            _check_mission_complete(character, mission_id)


def _check_mission_complete(character, mission_id):
    """
    Check if all objectives for *mission_id* are complete.

    If so, notifies the character that the mission is ready to turn in.
    """
    log = character.db.mission_log
    if not log:
        return

    entry = log.get(mission_id)
    if not entry or entry.get("state") != "in_progress":
        return

    objectives = entry.get("objectives", [])
    if not objectives:
        return

    all_done = all(
        obj.get("current", 0) >= obj.get("required", 1) for obj in objectives
    )

    if all_done:
        mission_def = MISSIONS.get(mission_id, {})
        giver = mission_def.get("giver_npc", "the mission giver")
        title = mission_def.get("title", mission_id)
        character.msg(
            f"|gAll objectives complete!|n Return to {giver} to finalise "
            f"'{title}'. (Type: |wcomplete {title}|n)"
        )


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _mission_title(mission_id):
    """Return the human-readable title for a mission_id, or the id itself."""
    return MISSIONS.get(mission_id, {}).get("title", mission_id)
