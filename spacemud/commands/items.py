"""
Item commands: get, drop, inventory, equip.
"""

from evennia.commands.command import Command

from utils.events import fire_event


class CmdGet(Command):
    """
    Pick up an artifact from the room.

    Usage:
      get <item>
      take <item>
      collect <item>

    Moves the named artifact from the current room into your inventory.
    """

    key = "get"
    aliases = ["take", "collect"]
    help_category = "General"

    def func(self):
        if not self.args:
            self.caller.msg("Get what? Usage: get <item>")
            return

        target = self.caller.search(self.args.strip(), location=self.caller.location)
        if not target:
            return  # search() sends "not found" message automatically

        target.move_to(self.caller)
        self.caller.msg(f"Artifact acquired: {target.name}.")
        # Fire event for mission tracking
        fire_event("artifact_collected", character=self.caller, item=target)


class CmdDrop(Command):
    """
    Drop an artifact from your inventory.

    Usage:
      drop <item>

    Moves the named artifact from your inventory to the current room.
    """

    key = "drop"
    help_category = "General"

    def func(self):
        if not self.args:
            self.caller.msg("Drop what? Usage: drop <item>")
            return

        target = self.caller.search(self.args.strip(), location=self.caller)
        if not target:
            return

        target.move_to(self.caller.location)
        self.caller.msg(f"Artifact deposited: {target.name}.")


class CmdInventory(Command):
    """
    List everything you are carrying.

    Usage:
      inventory
      inv
      i

    Displays all artifacts currently in your inventory.
    """

    key = "inventory"
    aliases = ["inv", "i"]
    help_category = "General"

    def func(self):
        items = self.caller.contents
        if not items:
            self.caller.msg("Carrying: nothing.")
            return

        lines = ["|wCarrying:|n"]
        for item in items:
            lines.append(f"  {item.name}")
        self.caller.msg("\n".join(lines))


class CmdEquip(Command):
    """
    Install a component from your inventory.

    Usage:
      equip <item>
      install <item>
      mount <item>

    Applies the stat modifiers of an equippable component to your unit.
    The component must be in your inventory and must be equippable.
    """

    key = "equip"
    aliases = ["install", "mount"]
    help_category = "General"

    def func(self):
        if not self.args:
            self.caller.msg("Equip what? Usage: equip <item>")
            return

        target = self.caller.search(self.args.strip(), location=self.caller)
        if not target:
            return

        if not target.db.equippable:
            self.caller.msg("Cannot install that component.")
            return

        target.apply_modifiers(self.caller)
        self.caller.msg(f"Component installed: {target.name}.")
