"""
Mission commands: talk, complete, missions, accept.
"""

from evennia.commands.command import Command
from evennia.utils.utils import inherits_from


class CmdTalk(Command):
    """
    Talk to an NPC in the current room.

    Usage:
      talk <npc>

    Initiates dialogue with the named NPC. Mission givers will show
    available missions when spoken to.
    """

    key = "talk"
    help_category = "Missions"

    def func(self):
        if not self.args:
            self.caller.msg("Talk to whom? Usage: talk <npc>")
            return

        target = self.caller.search(self.args.strip(), location=self.caller.location)
        if not target or not inherits_from(target, "typeclasses.objects.NPC"):
            self.caller.msg("No unit by that designation here.")
            return

        target.at_talk(self.caller)


class CmdComplete(Command):
    """
    Turn in a completed mission.

    Usage:
      complete <mission title>

    Completes the named mission if all objectives are finished and you
    are in the same room as the mission giver. Grants XP and credits.
    """

    key = "complete"
    help_category = "Missions"

    def func(self):
        if not self.args:
            self.caller.msg("Complete which mission? Usage: complete <mission title>")
            return

        mission_title = self.args.strip()
        from utils.missions import try_complete_mission
        try_complete_mission(self.caller, mission_title)


class CmdMissions(Command):
    """
    View your mission log.

    Usage:
      missions
      log
      journal

    Displays all missions in your log, grouped by state (active,
    completed).
    """

    key = "missions"
    aliases = ["log", "journal"]
    help_category = "Missions"

    def func(self):
        log = self.caller.db.mission_log
        if not log:
            self.caller.msg("Mission log: empty.")
            return

        from world.missions import MISSIONS

        in_progress = []
        completed = []

        for mission_id, entry in log.items():
            state = entry.get("state", "not_started")
            mission_def = MISSIONS.get(mission_id, {})
            title = mission_def.get("title", mission_id)
            objectives = entry.get("objectives", [])

            if state == "in_progress":
                in_progress.append((title, objectives))
            elif state == "completed":
                completed.append((title, objectives))

        lines = ["|w--- Mission Log ---|n"]

        if in_progress:
            lines.append("\n|yActive:|n")
            for title, objectives in in_progress:
                lines.append(f"  |w{title}|n")
                for obj in objectives:
                    current = obj.get("current", 0)
                    required = obj.get("required", 1)
                    target = obj.get("target", "?")
                    obj_type = obj.get("type", "?")
                    lines.append(
                        f"    - [{obj_type}] {target}: {current}/{required}"
                    )

        if completed:
            lines.append("\n|gCompleted:|n")
            for title, _ in completed:
                lines.append(f"  |w{title}|n |g[DONE]|n")

        if not in_progress and not completed:
            self.caller.msg("Mission log: empty.")
            return

        self.caller.msg("\n".join(lines))


class CmdAccept(Command):
    """
    Accept a mission offered by an NPC.

    Usage:
      accept <mission_id>

    Accepts the named mission and adds it to your mission log.
    You must have spoken to the mission giver first to see available missions.
    """

    key = "accept"
    help_category = "Missions"

    def func(self):
        if not self.args:
            self.caller.msg("Accept which mission? Usage: accept <mission_id>")
            return

        mission_id = self.args.strip()
        from utils.missions import accept_mission
        accept_mission(self.caller, mission_id)
