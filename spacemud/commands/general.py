"""
General commands: status, repair, scan, help.
"""

from evennia.commands.command import Command
from evennia.utils.utils import inherits_from

from utils.events import fire_event


class CmdStatus(Command):
    """
    View your character's stats.

    Usage:
      status
      stat
      sc

    Displays your unit's designation, level, XP, integrity, power,
    processing, shielding, repair level, and credits.
    """

    key = "status"
    aliases = ["stat", "sc"]
    help_category = "General"

    def func(self):
        c = self.caller
        self.caller.msg(
            f"|wDesignation:|n {c.name}\n"
            f"|wLevel:|n {c.db.level}  |wXP:|n {c.db.experience}\n"
            f"|wIntegrity:|n {c.db.integrity}/{c.db.max_integrity}  "
            f"|wPower:|n {c.db.power}/{c.db.max_power}\n"
            f"|wProcessing:|n {c.db.processing}  |wShielding:|n {c.db.shielding}\n"
            f"|wRepair Level:|n {c.db.repair_level}  |wCredits:|n {c.db.credits}"
        )


class CmdRepair(Command):
    """
    Repair a damaged object in the current room.

    Usage:
      repair <object>

    Checks repair level requirement, consumes required components
    from inventory, and marks the object as repaired.
    """

    key = "repair"
    help_category = "General"

    def func(self):
        if not self.args:
            self.caller.msg("Repair what? Usage: repair <object>")
            return

        target = self.caller.search(self.args.strip(), location=self.caller.location)
        if not target or not inherits_from(target, "typeclasses.objects.RepairableObject"):
            self.caller.msg("No repairable object by that designation.")
            return

        if target.db.repaired:
            self.caller.msg("Already repaired.")
            return

        # Check repair level
        required = target.db.repair_level_required or 1
        if self.caller.db.repair_level < required:
            self.caller.msg(
                f"Repair level insufficient. Required: {required}. "
                f"Current: {self.caller.db.repair_level}."
            )
            return

        # Check and consume repair cost (artifacts from inventory)
        cost = target.db.repair_cost or {}
        for item_name, qty in cost.items():
            carried = [
                obj for obj in self.caller.contents
                if obj.name.lower() == item_name.lower()
            ]
            if len(carried) < qty:
                self.caller.msg(
                    f"Insufficient components. Need {qty}x {item_name}."
                )
                return

        # Consume components
        for item_name, qty in cost.items():
            carried = [
                obj for obj in self.caller.contents
                if obj.name.lower() == item_name.lower()
            ]
            for obj in carried[:qty]:
                obj.delete()

        # Deduct power cost if software repair
        power_cost = target.db.power_cost or 0
        if power_cost:
            self.caller.db.power = max(0, self.caller.db.power - power_cost)

        # Mark repaired
        target.db.repaired = True
        msg = target.db.on_repair_message or f"{target.name} repaired."
        self.caller.location.msg_contents(msg)
        fire_event("repair_completed", character=self.caller, target=target)


class CmdScan(Command):
    """
    Scan the current room.

    Usage:
      scan

    Re-sends the current room description. Equivalent to look.
    """

    key = "scan"
    help_category = "General"

    def func(self):
        self.caller.execute_cmd("look")


class CmdHelp(Command):
    """
    Get help on commands.

    Usage:
      help
      help <command>
      ? <command>

    Without arguments, lists all available commands grouped by category.
    With a command name, shows usage and description for that command.
    """

    key = "help"
    aliases = ["?"]
    help_category = "General"

    def func(self):
        if self.args:
            self._show_command_help(self.args.strip())
        else:
            self._list_all_commands()

    def _show_command_help(self, cmd_name):
        """Show help for a specific command."""
        cmd_name_lower = cmd_name.lower()

        # Search through the current cmdset for a matching command
        cmdset = self.caller.cmdset.current
        if cmdset is None:
            self.caller.msg("No commands available.")
            return

        match = None
        for cmd in cmdset.commands:
            if cmd.key.lower() == cmd_name_lower:
                match = cmd
                break
            # Check aliases
            if hasattr(cmd, "aliases") and cmd.aliases:
                for alias in cmd.aliases:
                    if alias.lower() == cmd_name_lower:
                        match = cmd
                        break
            if match:
                break

        if not match:
            self.caller.msg(
                f"No help found for '{cmd_name}'. "
                f"Type |whelp|n for a list of all commands."
            )
            return

        # Display the command's docstring as help text
        doc = match.__doc__ or "No description available."
        # Clean up indentation
        lines = doc.strip().splitlines()
        cleaned = "\n".join(line.strip() for line in lines)
        self.caller.msg(
            f"|w=== Help: {match.key} ===|n\n{cleaned}"
        )

    def _list_all_commands(self):
        """List all available commands grouped by help_category."""
        cmdset = self.caller.cmdset.current
        if cmdset is None:
            self.caller.msg("No commands available.")
            return

        # Group commands by help_category
        categories = {}
        for cmd in sorted(cmdset.commands, key=lambda c: c.key):
            category = getattr(cmd, "help_category", "General") or "General"
            categories.setdefault(category, []).append(cmd)

        lines = ["|w=== Available Commands ===|n"]
        for category in sorted(categories):
            cmds = categories[category]
            cmd_names = []
            for cmd in cmds:
                name = cmd.key
                if hasattr(cmd, "aliases") and cmd.aliases:
                    name += f" ({', '.join(cmd.aliases)})"
                cmd_names.append(name)
            lines.append(f"\n|y{category}:|n")
            lines.append("  " + "  ".join(cmd_names))

        lines.append(
            "\nType |whelp <command>|n for detailed help on a specific command."
        )
        self.caller.msg("\n".join(lines))
