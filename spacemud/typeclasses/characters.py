"""
Characters

Characters are (by default) Objects setup to be puppeted by Accounts.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""

from evennia.objects.objects import DefaultCharacter

from .objects import ObjectParent


class Character(ObjectParent, DefaultCharacter):
    """
    The Character just re-implements some of the Object's methods and hooks
    to represent a Character entity in-game.

    See mygame/typeclasses/objects.py for a list of
    properties and methods available on all Object child classes like this.

    """

    pass


class RobotCharacter(DefaultCharacter):
    """
    A robot universe player character typeclass.

    Extends Evennia's DefaultCharacter with robot-universe attributes
    for stats, state tracking, mission logging, and a configurable prompt.

    Attributes (all persisted via Evennia's db.* system):
        level (int): Character level, starts at 1.
        experience (int): Accumulated experience points.
        integrity (int): Current integrity points.
        max_integrity (int): Maximum integrity points.
        power (int): Current power points.
        max_power (int): Maximum power points.
        processing (int): Base processing stat.
        shielding (int): Base shielding stat.
        repair_level (int): Repair capability level.
        credits (int): In-game currency.
        player_state (str): One of "active", "idle", "combat", "offline".
        idle_message (str): Optional message shown when character is idle.
        mission_log (dict): Maps mission_id to MissionEntry dict.
        prompt_template (str): Format string for the status prompt.
    """

    def at_object_creation(self):
        """Called once when the character object is first created."""
        # Core stats
        self.db.level = 1
        self.db.experience = 0
        self.db.integrity = 100
        self.db.max_integrity = 100
        self.db.power = 50
        self.db.max_power = 50
        self.db.processing = 10
        self.db.shielding = 5
        self.db.repair_level = 1
        self.db.credits = 0
        # State
        self.db.player_state = "active"    # active | idle | combat | offline
        self.db.idle_message = ""
        # Mission tracking
        self.db.mission_log = {}           # {mission_id: MissionEntry dict}
        # Chassis and profession (Phase 2)
        self.db.chassis = None             # None until player selects at Chassis Terminal
        self.db.profession = None          # None until player selects at Protocol Terminal
        self.db.skills = []                # list of unlocked skill IDs
        self.db.skill_cooldowns = {}       # {skill_id: timestamp_when_usable}
        self.db.bonus_damage = 0           # temporary bonus from skills
        self.db.pvp_kills = 0              # PVP kill count
        # Prompt
        self.db.prompt_template = "[INT:{integrity}/{max_integrity} PWR:{power}/{max_power}]> "

    def at_after_move(self, source_location, **kwargs):
        """
        Called after the character successfully moves to a new location.

        Fires the unit_enters_room event by calling at_unit_enter on
        the destination room, allowing room-specific logic to execute.

        Args:
            source_location: The room the character moved from.
            **kwargs: Additional keyword arguments passed by Evennia.
        """
        if self.location:
            self.location.at_unit_enter(self)

    def return_appearance(self, looker, **kwargs):
        """
        Override to add robot-voice sensor scan header to room look output.

        Args:
            looker: The object (character) doing the looking.
            **kwargs: Additional keyword arguments passed by Evennia.

        Returns:
            str: The formatted appearance string with sensor scan header.
        """
        base_appearance = super().return_appearance(looker, **kwargs)
        header = "|b--- SENSOR SCAN ---|n\n"
        return header + base_appearance

    def get_prompt(self):
        """
        Return the formatted status prompt string for this character.

        Returns:
            str: Prompt string with current integrity and power values filled in.
        """
        return self.db.prompt_template.format(
            integrity=self.db.integrity,
            max_integrity=self.db.max_integrity,
            power=self.db.power,
            max_power=self.db.max_power,
        )

    def award_xp(self, amount):
        """
        Award experience points to the character and check for level-up.

        XP threshold to reach the next level is ``current_level * 100``
        (e.g. level 1→2 requires 100 XP, level 2→3 requires 200 XP, etc.).
        Maximum level is 20. Multiple level-ups from a single award are
        handled by looping until the threshold is no longer met.

        On each level-up the character's max_integrity increases by 10 and
        processing increases by 1 as a small stat bonus. If a profession is
        set, the profession growth table is used instead.

        Args:
            amount (int): The number of experience points to award.
        """
        self.db.experience += amount
        self.msg(f"|yProcessing log: +{amount} XP.|n")
        # Check for level-up — loop to handle multiple levels in one award
        while self.db.level < 20:
            xp_needed = self.db.level * 100
            if self.db.experience >= xp_needed:
                self.db.level += 1
                # Apply profession growth if set, otherwise flat defaults
                if self.db.profession:
                    from world.professions import PROFESSIONS
                    growth = PROFESSIONS[self.db.profession]["growth"]
                    for stat, value in growth.items():
                        current = getattr(self.db, stat, 0)
                        setattr(self.db, stat, current + value)
                else:
                    # Phase 1 flat growth
                    self.db.max_integrity += 10
                    self.db.processing += 1
                self.db.integrity = min(self.db.integrity + 10, self.db.max_integrity)
                self.msg(f"|gSystem upgrade. Level {self.db.level} reached.|n")
                # Check for new skill unlocks
                if self.db.profession:
                    from world.professions import PROFESSIONS
                    skills = PROFESSIONS[self.db.profession].get("skills", {})
                    for level, skill_id in skills.items():
                        if self.db.level >= int(level) and skill_id not in (self.db.skills or []):
                            self.db.skills.append(skill_id)
                            self.msg(f"|gSkill unlocked: {skill_id}.|n")
            else:
                break

    def install_chassis(self, chassis_id):
        """
        Apply chassis stat modifiers permanently. One-time only.

        Args:
            chassis_id (str): Key from world.chassis.CHASSIS dict.

        Returns:
            bool: True if installed, False if rejected.
        """
        if self.db.chassis:
            self.msg("Chassis already installed.")
            return False
        from world.chassis import CHASSIS
        chassis = CHASSIS.get(chassis_id)
        if not chassis:
            self.msg("Unknown chassis type.")
            return False
        # Apply stat modifiers
        for stat, value in chassis["stat_modifiers"].items():
            current = getattr(self.db, stat, 0)
            setattr(self.db, stat, current + value)
        self.db.chassis = chassis_id
        self.msg(f"Chassis installed: {chassis['name']}. Systems recalibrating.")
        # Start passive scripts if applicable
        if chassis_id == "repair":
            from evennia.utils.create import create_script
            create_script("typeclasses.scripts.SelfRepairScript", obj=self, persistent=True)
        return True

    def install_profession(self, profession_id):
        """
        Apply profession permanently. Requires chassis and level >= 3.

        Args:
            profession_id (str): Key from world.professions.PROFESSIONS dict.

        Returns:
            bool: True if installed, False if rejected.
        """
        if self.db.profession:
            self.msg("Protocol already installed.")
            return False
        if not self.db.chassis:
            self.msg("Chassis required before protocol installation.")
            return False
        if self.db.level < 3:
            self.msg("Insufficient level. Required: 3.")
            return False
        from world.professions import PROFESSIONS
        prof = PROFESSIONS.get(profession_id)
        if not prof:
            self.msg("Unknown protocol.")
            return False
        self.db.profession = profession_id
        # Unlock any skills for current level
        for level, skill_id in prof.get("skills", {}).items():
            if self.db.level >= int(level) and skill_id not in (self.db.skills or []):
                self.db.skills.append(skill_id)
                self.msg(f"Skill unlocked: {skill_id}.")
        self.msg(f"Protocol installed: {prof['name']}. Operational parameters updated.")
        return True
