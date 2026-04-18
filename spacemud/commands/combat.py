"""
Combat commands: attack and flee.
"""

import random

from evennia.commands.command import Command
from evennia.utils.create import create_script
from evennia.utils.utils import inherits_from


class CmdAttack(Command):
    """
    Engage a hostile in combat.

    Usage:
      attack <target>
      engage <target>
      fight <target>

    Initiates combat with a hostile NPC in your current location.
    """

    key = "attack"
    aliases = ["engage", "fight"]
    help_category = "Combat"

    def func(self):
        if not self.args:
            self.caller.msg("Engage what? Usage: attack <target>")
            return

        if self.caller.db.player_state == "combat":
            self.caller.msg("Combat already active.")
            return

        target = self.caller.search(self.args.strip(), location=self.caller.location)
        if not target:
            return

        # Check if target is a hostile (PVE)
        if inherits_from(target, "typeclasses.objects.Hostile"):
            self._start_combat(target)
            return

        # Check if target is another player (PVP)
        if target.has_account and target != self.caller:
            if not self.caller.location.db.pvp_zone:
                self.caller.msg("Combat protocol restricted in this zone.")
                return
            self._start_combat(target)
            return

        self.caller.msg("No valid target by that designation.")

    def _start_combat(self, target):
        """Start a combat script between caller and target."""
        script = create_script(
            "typeclasses.scripts.CombatScript",
            obj=self.caller,
            persistent=True,
        )
        script.db.attacker = self.caller
        script.db.defender = target
        self.caller.db.player_state = "combat"
        self.caller.msg(f"Engaging {target.name}.")


class CmdFlee(Command):
    """
    Attempt to flee from combat.

    Usage:
      flee

    Moves you to a random adjacent room and ends combat.
    If there are no exits, you cannot escape.
    """

    key = "flee"
    help_category = "Combat"

    def func(self):
        exits = self.caller.location.exits
        if not exits:
            self.caller.msg("No exit vector found.")
            return

        exit_obj = random.choice(exits)
        self.caller.move_to(exit_obj.destination)

        # Stop any active combat script
        for script in self.caller.scripts.all():
            if script.key == "combat_script":
                script.stop()

        self.caller.db.player_state = "active"
        self.caller.msg("Disengaged.")
