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
        """Start a combat script between caller and target.

        Order matters here. The CombatScript has ``start_delay=False`` so its
        first ``at_repeat`` round fires *immediately* when the timer starts.
        We therefore (1) create the script with ``autostart=False``,
        (2) set the combatants and the caller's ``player_state`` *before*
        starting the timer, then (3) start it with an explicit ``interval``
        and ``start_delay`` so the timer is unambiguously configured (a
        persistent script created with ``autostart=False`` will not otherwise
        have its timer running). If any of this happened out of order the
        first round could run before combatants/state were set, which is the
        original "combat doesn't tick" bug.
        """
        script = create_script(
            "typeclasses.scripts.CombatScript",
            obj=self.caller,
            persistent=True,
            autostart=False,
        )
        script.db.attacker = self.caller
        script.db.defender = target
        self.caller.db.player_state = "combat"
        # Explicitly (re)configure and start the timer. Passing interval and
        # start_delay makes the ticking behaviour independent of any prior
        # timer state left over from create_script(autostart=False).
        script.start(interval=2, start_delay=False)
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



class CmdQuit(Command):
    """
    Disconnect from the station.

    Usage:
      quit
      logout

    Safely powers down your unit and disconnects.
    """

    key = "quit"
    aliases = ["logout"]
    help_category = "General"

    def func(self):
        self.caller.msg("|bSystems powering down. Unit state preserved. Reconnect at any time.|n")
        self.caller.db.player_state = "offline"
        self.caller.account.disconnect_session_from_account(self.session)
