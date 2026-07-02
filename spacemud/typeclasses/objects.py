"""
Object

The Object is the class for general items in the game world.

Use the ObjectParent class to implement common features for *all* entities
with a location in the game world (like Characters, Rooms, Exits).

"""

from evennia.objects.objects import DefaultObject


class ObjectParent:
    """
    This is a mixin that can be used to override *all* entities inheriting at
    some distance from DefaultObject (Objects, Exits, Characters and Rooms).

    Just add any method that exists on `DefaultObject` to this class. If one
    of the derived classes has itself defined that same hook already, that will
    take precedence.

    """


class Object(ObjectParent, DefaultObject):
    """
    This is the root Object typeclass, representing all entities that
    have an actual presence in-game.
    """

    pass


class Artifact(DefaultObject):
    """
    Base typeclass for all pickable artifacts in the game world.
    """

    def at_object_creation(self):
        self.db.item_type = "misc"         # component | data | consumable | quest | misc
        self.db.weight = 1.0
        self.db.equippable = False
        self.db.equip_slot = None          # chassis_mod | power_cell | etc.
        self.db.stat_modifiers = {}        # {"processing": 5, "shielding": 2}


class Equipment(Artifact):
    """
    Equippable artifact that applies stat modifiers to a character when installed.
    """

    def at_object_creation(self):
        super().at_object_creation()
        self.db.equippable = True

    def apply_modifiers(self, character):
        """Apply stat modifiers to the given character."""
        for stat, value in self.db.stat_modifiers.items():
            current = getattr(character.db, stat, 0) or 0
            setattr(character.db, stat, current + value)

    def remove_modifiers(self, character):
        """Remove stat modifiers from the given character."""
        for stat, value in self.db.stat_modifiers.items():
            current = getattr(character.db, stat, 0) or 0
            setattr(character.db, stat, current - value)


class Hostile(DefaultObject):
    """
    An enemy NPC that can be attacked by players. Drops salvage on death and respawns.
    """

    def at_object_creation(self):
        self.db.integrity = 50
        self.db.max_integrity = 50
        self.db.processing = 8
        self.db.shielding = 3
        self.db.xp_reward = 50
        self.db.credits_reward = 10
        self.db.salvage_items = []         # list of artifact typeclass paths to spawn on death
        self.db.home_location = None       # dbref of home room
        self.db.respawn_delay = 300        # seconds
        self.db.chassis = None             # for passive checks in combat
        # Hostiles cannot be picked up
        self.locks.add("get:false()")

    def at_death(self, killer):
        """Called when integrity reaches 0. Spawns salvage, fires hostile_destroyed event."""
        self.spawn_salvage()
        killer.award_xp(self.db.xp_reward)
        killer.db.credits += self.db.credits_reward
        # Fire event for mission tracking
        from utils.events import fire_event
        fire_event("hostile_destroyed", killer=killer, hostile=self)
        # Schedule respawn
        self.scripts.add("typeclasses.scripts.RespawnScript")
        self.location = None               # remove from world until respawn

    def spawn_salvage(self):
        """Spawn all salvage items at the hostile's current location."""
        from evennia import create_object
        for item_typeclass in self.db.salvage_items:
            create_object(item_typeclass, location=self.location)


class NPC(DefaultObject):
    """
    A non-player character. Can be ambient, a mission giver, or a vendor.
    """

    def at_object_creation(self):
        self.db.role = "ambient"           # ambient | mission_giver | vendor | chassis_terminal | protocol_terminal
        self.db.home_location = None
        self.db.dialogue = ""              # shown when unit talks to them
        self.db.missions_offered = []      # list of mission_ids
        # NPCs cannot be picked up
        self.locks.add("get:false()")

    def at_talk(self, character):
        """Called by the talk command."""
        character.msg(self.db.dialogue)
        if self.db.role == "mission_giver":
            from utils.missions import show_available_missions
            show_available_missions(character, self)
        elif self.db.role == "chassis_terminal":
            if character.db.chassis:
                character.msg("Chassis already installed.")
                return
            from world.chassis import CHASSIS
            lines = ["|wAvailable chassis:|n"]
            for cid, chassis in CHASSIS.items():
                mods = ", ".join(f"{s}: {v:+d}" for s, v in chassis["stat_modifiers"].items())
                lines.append(f"\n  |y{cid}|n — {chassis['name']}")
                lines.append(f"    {chassis['description']}")
                lines.append(f"    Stats: {mods}")
                lines.append(f"    Passive: {chassis['passive_description']}")
            lines.append(f"\nType |wselect <chassis>|n to install.")
            character.msg("\n".join(lines))
        elif self.db.role == "protocol_terminal":
            if character.db.profession:
                character.msg("Protocol already installed.")
                return
            if not character.db.chassis:
                character.msg("Chassis required before protocol installation.")
                return
            if (character.db.level or 1) < 3:
                character.msg(f"Insufficient level. Required: 3. Current: {character.db.level or 1}.")
                return
            from world.professions import PROFESSIONS
            lines = ["|wAvailable protocols:|n"]
            for pid, prof in PROFESSIONS.items():
                growth = ", ".join(f"{s}: +{v}" for s, v in prof["growth"].items())
                skills = ", ".join(f"Lv{lv}: {sid}" for lv, sid in prof.get("skills", {}).items())
                lines.append(f"\n  |y{pid}|n — {prof['name']}")
                lines.append(f"    {prof['description']}")
                lines.append(f"    Growth: {growth}")
                lines.append(f"    Skills: {skills or 'None'}")
            lines.append(f"\nType |wselect <protocol>|n to install.")
            character.msg("\n".join(lines))


class RepairableObject(DefaultObject):
    """
    Objects in the station that can be repaired by the player.
    Repair state persists across restarts.
    """

    def at_object_creation(self):
        self.db.repaired = False
        self.db.repair_level_required = 1  # minimum unit repair_level to attempt
        self.db.repair_cost = {}           # {"Power Cell": 2, "Circuit Component": 1}
        self.db.power_cost = 0             # power deducted for software-only repairs
        self.db.on_repair_message = ""     # message sent to room when repaired
        self.db.requires_repaired = None   # key name of prerequisite RepairableObject
        self.db.desc_damaged = ""          # room description when damaged
        self.db.desc_repaired = ""         # room description when repaired
        # Repairable objects cannot be picked up
        self.locks.add("get:false()")
