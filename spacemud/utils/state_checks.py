# utils/state_checks.py
"""
Unit state enforcement helpers.

Call check_state(caller, cmd_key) from a command's at_pre_cmd or func.
Returns True if the command should be blocked, False if allowed.
"""

COMBAT_RESTRICTED = {"repair", "missions", "complete", "talk", "select", "idle", "accept"}
OFFLINE_ALLOWED = {"scan", "look", "help", "quit"}

def check_state(caller, cmd_key):
    """
    Check if the command is allowed given the caller's player_state.
    Returns an error message string if blocked, or None if allowed.
    Also handles idle→active transition.
    """
    state = caller.db.player_state
    cmd = cmd_key.lower()

    # Idle → any command returns to active
    if state == "idle":
        caller.db.player_state = "active"
        caller.db.idle_message = ""
        if caller.location:
            caller.location.msg_contents(
                f"{caller.name} is no longer idle.", exclude=caller
            )

    # Combat restrictions
    if state == "combat" and cmd in COMBAT_RESTRICTED:
        return f"Command restricted during combat: {cmd}"

    # Offline restrictions
    if state == "offline" and cmd not in OFFLINE_ALLOWED:
        return "Systems offline. Only scan available."

    return None
