"""
Room

Rooms are simple containers that has no location of their own.

"""

from evennia.objects.objects import DefaultRoom
from evennia.utils.utils import inherits_from

from .objects import ObjectParent


class Room(ObjectParent, DefaultRoom):
    """
    Rooms are like any Object, except their location is None
    (which is default). They also use basetype_setup() to
    add locks so they cannot be puppeted or picked up.
    (to change that, use at_object_creation instead)

    See mygame/typeclasses/objects.py for a list of
    properties and methods available on all Objects.
    """

    pass


class StationRoom(DefaultRoom):
    """
    A robot universe station room typeclass.

    Attributes:
        db.zone (str): The zone this room belongs to (e.g. "central_station",
            "outer_zone"). Defaults to "unknown".
        db.pvp_zone (bool): Whether PvP combat is allowed in this room.
            Defaults to False.
    """

    def at_object_creation(self):
        """Set default station room attributes on first creation."""
        super().at_object_creation()
        self.db.zone = "unknown"
        self.db.pvp_zone = False

    def at_unit_enter(self, character):
        """
        Event hook called when a unit enters this room.

        Override in subclasses to add room-specific behaviour (e.g. triggering
        an ambush, displaying a special message, starting a script).

        Args:
            character: The character that just entered the room.
        """
        pass

    def return_appearance(self, looker, **kwargs):
        """
        Return a formatted string describing the room to *looker*.

        Sections shown (in order):
        - Room name (bold)
        - Room description
        - Zone tag (e.g. "[Zone: Central Station]")
        - Exits
        - Units present (excluding the looker)
        - Hostiles present
        - Artifacts present

        Args:
            looker: The character looking at the room.
            **kwargs: Passed through from Evennia internals.

        Returns:
            str: The formatted room description.
        """
        if not looker:
            return ""

        lines = []

        # Room name (bold)
        lines.append(f"|w{self.get_display_name(looker)}|n")

        # Room description
        desc = self.db.desc
        if desc:
            lines.append(str(desc))

        # Zone tag
        zone = self.db.zone or "unknown"
        lines.append(f"|y[Zone: {zone.replace('_', ' ').title()}]|n")

        # Exits
        exits = [
            obj for obj in self.contents
            if obj.destination  # Evennia exits have a destination attribute
        ]
        if exits:
            exit_names = ", ".join(e.get_display_name(looker) for e in exits)
            lines.append(f"|gExits:|n {exit_names}")
        else:
            lines.append("|gExits:|n None")

        # Categorise contents (excluding exits and the looker)
        players = []
        hostiles = []
        items = []

        for obj in self.contents:
            if obj is looker:
                continue
            if obj.destination:
                # It's an exit — already handled
                continue
            if inherits_from(obj, "typeclasses.objects.Hostile"):
                hostiles.append(obj)
            elif obj.has_account:
                # It's a connected player character
                players.append(obj)
            elif inherits_from(obj, "evennia.objects.objects.DefaultCharacter"):
                # NPC or offline character — treat as player-like for display
                players.append(obj)
            else:
                items.append(obj)

        # Units present
        if players:
            player_names = ", ".join(p.get_display_name(looker) for p in players)
            lines.append(f"|cUnits:|n {player_names}")

        # Hostiles present
        if hostiles:
            hostile_names = ", ".join(h.get_display_name(looker) for h in hostiles)
            lines.append(f"|rHostiles:|n {hostile_names}")

        # Artifacts present
        if items:
            item_names = ", ".join(i.get_display_name(looker) for i in items)
            lines.append(f"|wArtifacts:|n {item_names}")

        return "\n".join(lines)
