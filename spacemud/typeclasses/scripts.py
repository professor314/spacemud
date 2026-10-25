"""
Scripts

Scripts are powerful jacks-of-all-trades. They have no in-game
existence and can be used to represent persistent game systems in some
circumstances. Scripts can also have a time component that allows them
to "fire" regularly or a limited number of times.

There is generally no "tree" of Scripts inheriting from each other.
Rather, each script tends to inherit from the base Script class and
just overloads its hooks to have it perform its function.

"""

import random

import evennia
from evennia.scripts.scripts import DefaultScript
from evennia.utils import logger


class Script(DefaultScript):
    """
    This is the base TypeClass for all Scripts.
    """

    pass


class CombatScript(DefaultScript):
    """
    Drives the combat loop between an attacker (player character) and a
    defender (hostile NPC). Fires every 2 seconds, running one round of
    combat per tick.

    Each round:
      1. Attacker hits defender — damage = max(1, processing - shielding + randint(-2, 2))
      2. If defender dies, call at_death, award XP/credits, stop script.
      3. Defender hits attacker — same formula.
      4. If attacker dies, move to Repair Bay at 25% integrity, stop script.
    """

    def at_script_creation(self):
        self.key = "combat_script"
        self.interval = 2          # seconds between combat rounds
        self.persistent = True
        self.db.attacker = None    # RobotCharacter
        self.db.defender = None    # Hostile

    def at_repeat(self):
        """Called every 2 seconds. Runs one full combat round."""
        attacker = self.db.attacker
        defender = self.db.defender

        # Validate both combatants are still present and valid
        if not attacker or not defender:
            self.stop()
            return

        # Guard against deleted/invalid objects
        try:
            _ = attacker.db.integrity
            _ = defender.db.integrity
        except Exception:
            self.stop()
            return

        # --- Attacker hits defender ---
        bonus = attacker.db.bonus_damage or 0
        dmg = max(1, attacker.db.processing + bonus - defender.db.shielding + random.randint(-2, 2))
        if bonus:
            attacker.db.bonus_damage = 0
        # Heavy chassis passive: damage reduction for defender
        if defender.db.chassis == "heavy":
            dmg = max(1, dmg - 2)
        defender.db.integrity -= dmg
        attacker.msg(
            f"Processing output: {dmg}. "
            f"Target integrity reduced. Target integrity: {defender.db.integrity}."
        )
        if attacker.location:
            attacker.location.msg_contents(
                f"{attacker.name} engages {defender.name}.",
                exclude=attacker,
            )

        if defender.db.integrity <= 0:
            defender.at_death(attacker)
            attacker.db.player_state = "active"
            attacker.msg("Target neutralised.")
            self.stop()
            return

        # --- Defender hits attacker ---
        dmg = max(1, defender.db.processing - attacker.db.shielding + random.randint(-2, 2))
        # Heavy chassis passive: damage reduction for attacker
        if attacker.db.chassis == "heavy":
            dmg = max(1, dmg - 2)
        attacker.db.integrity -= dmg
        attacker.msg(
            f"Impact detected. Integrity reduced by {dmg}. "
            f"Current integrity: {attacker.db.integrity}."
        )
        if attacker.location:
            attacker.location.msg_contents(
                f"{defender.name} strikes {attacker.name}!",
                exclude=attacker,
            )

        if attacker.db.integrity <= 0:
            # Unit death — transport to Repair Bay
            attacker.db.player_state = "offline"
            attacker.db.integrity = max(1, attacker.db.max_integrity // 4)

            # PVP death handling — if defender is a player character
            if defender.has_account:
                xp_penalty = int(attacker.db.experience * 0.1)
                attacker.db.experience = max(0, attacker.db.experience - xp_penalty)
                defender.db.pvp_kills = (defender.db.pvp_kills or 0) + 1
                attacker.msg(f"Destroyed by {defender.name}. XP penalty: -{xp_penalty}.")
                defender.msg(f"{attacker.name} destroyed. PVP kill recorded.")

            repair_bay = self._find_repair_bay()
            if repair_bay:
                attacker.move_to(repair_bay)
            else:
                logger.log_warn(
                    "CombatScript: No Repair Bay found. "
                    "Unit death location unchanged."
                )

            attacker.msg("Critical failure. Emergency reboot initiated. Repair Bay.")
            attacker.db.player_state = "active"
            self.stop()

    def _find_repair_bay(self):
        """
        Locate the Repair Bay room. Tries by name first,
        then falls back to any room tagged 'repair_bay'. Returns None if
        no suitable room is found.
        """
        # Primary: search for the Repair Bay room by name and typeclass
        results = evennia.search_object(
            "Repair Bay",
            typeclass="typeclasses.rooms.StationRoom",
        )
        if results:
            return results[0]

        # Fallback: any room tagged as repair_bay
        results = evennia.search_object("repair_bay", attribute_name="tags")
        if results:
            return results[0]

        return None


class RespawnScript(DefaultScript):
    """
    Fires once after `db.respawn_delay` seconds (default 300). Restores the
    attached hostile to full integrity and moves it back to its home location.

    Attach to a Hostile via:
        hostile.scripts.add("typeclasses.scripts.RespawnScript")
    """

    def at_script_creation(self):
        self.key = "respawn_script"
        # Use the hostile's configured respawn delay, or 300 s as default
        delay = None
        if self.obj:
            delay = self.obj.db.respawn_delay
        self.interval = delay if delay is not None else 300
        self.repeats = 1           # fire exactly once
        # Wait `interval` seconds before the (single) at_repeat call. Without
        # this, Evennia's default start_delay=False makes at_repeat fire
        # *immediately* when the script is added on death, respawning the
        # hostile instantly instead of after respawn_delay seconds. This was
        # the "hostile respawns instantly" bug.
        self.start_delay = True
        self.persistent = True

    def at_repeat(self):
        """Called once after the respawn delay. Restores hostile and repositions it."""
        hostile = self.obj
        if not hostile:
            self.stop()
            return

        hostile.db.integrity = hostile.db.max_integrity

        home = hostile.db.home_location
        if home:
            hostile.move_to(home)
        else:
            logger.log_warn(
                f"RespawnScript: {hostile.name} has no home_location set; "
                "respawn location unchanged."
            )

        self.stop()


class SelfRepairScript(DefaultScript):
    """
    Passive script for the Repair chassis. Ticks every 60 seconds and
    restores 1 integrity if the unit is not in combat and still has the
    repair chassis equipped.
    """

    def at_script_creation(self):
        self.key = "self_repair_script"
        self.interval = 60  # every 60 seconds
        self.persistent = True

    def at_repeat(self):
        unit = self.obj
        if not unit:
            self.stop()
            return
        # Only heal if not in combat and has repair chassis
        if unit.db.player_state == "combat":
            return
        if unit.db.chassis != "repair":
            self.stop()
            return
        if unit.db.integrity < unit.db.max_integrity:
            unit.db.integrity = min(unit.db.integrity + 1, unit.db.max_integrity)
            unit.msg("Self-repair: +1 integrity.")


class RepairDegradeScript(DefaultScript):
    """
    After a system is repaired, it degrades back to damaged state after
    a set interval (default 600 seconds / 10 minutes). This makes repairs
    repeatable, providing renewable XP sources.

    Attached to a RepairableObject when it's repaired.
    """

    def at_script_creation(self):
        self.key = "repair_degrade_script"
        self.interval = self.obj.db.degrade_delay if self.obj and self.obj.db.degrade_delay else 600
        self.repeats = 1
        # Wait the full degrade delay before the single at_repeat fires.
        # Without start_delay=True the system would degrade back to damaged
        # instantly on repair (Evennia start_delay defaults to False), same
        # root cause as the RespawnScript bug.
        self.start_delay = True
        self.persistent = True

    def at_repeat(self):
        """Called once after the degrade delay. Marks system as damaged again."""
        obj = self.obj
        if not obj:
            self.stop()
            return

        obj.db.repaired = False
        if obj.location:
            obj.location.msg_contents(
                f"|y{obj.name} flickers and sparks. Systems degrading. Repair required.|n"
            )
        self.stop()
