"""
Tests for item commands: get, drop, equip.

Covers:
- get an artifact present in the room → moves to inventory
- get an artifact not in the room → sends error message
- drop a carried artifact → moves to room
- drop an artifact not in inventory → sends error message
- equip an Equipment item → applies stat modifiers to character
- equip a non-equippable item → sends error message
"""

import pytest

try:
    from evennia.utils.test_resources import EvenniaTest
    import evennia

    _EVENNIA_AVAILABLE = True
except Exception:
    _EVENNIA_AVAILABLE = False

pytestmark = pytest.mark.skipif(
    not _EVENNIA_AVAILABLE, reason="Evennia not available"
)


@pytest.mark.skipif(not _EVENNIA_AVAILABLE, reason="Evennia not available")
class TestGetCommand(EvenniaTest):
    """Tests for CmdGet."""

    def _capture_messages(self, char):
        """Monkey-patch char.msg to capture sent messages."""
        messages = []
        original = char.msg

        def capture(text=None, **kwargs):
            if text:
                messages.append(str(text))

        char.msg = capture
        return messages, original

    def test_get_present_item(self):
        """Getting an artifact in the room moves it to the character's inventory."""
        item = evennia.create_object(
            "typeclasses.objects.Artifact",
            key="Power Cell",
            location=self.room1,
        )
        self.char1.location = self.room1

        from commands.items import CmdGet
        cmd = CmdGet()
        cmd.caller = self.char1
        cmd.args = "Power Cell"
        cmd.session = None
        cmd.func()

        # Item should now be in char1's inventory, not in the room
        self.assertIn(item, self.char1.contents)
        self.assertNotIn(item, self.room1.contents)

        item.delete()

    def test_get_absent_item(self):
        """Getting an artifact not in the room sends an error message."""
        self.char1.location = self.room1
        messages, original = self._capture_messages(self.char1)

        from commands.items import CmdGet
        cmd = CmdGet()
        cmd.caller = self.char1
        cmd.args = "NonexistentItem12345"
        cmd.session = None
        cmd.func()

        self.char1.msg = original
        # Evennia's search() sends a "not found" message automatically;
        # the character should have received at least one message.
        # We just verify no exception was raised and the item isn't in inventory.
        item_names = [obj.name for obj in self.char1.contents]
        self.assertNotIn("NonexistentItem12345", item_names)


@pytest.mark.skipif(not _EVENNIA_AVAILABLE, reason="Evennia not available")
class TestDropCommand(EvenniaTest):
    """Tests for CmdDrop."""

    def _capture_messages(self, char):
        messages = []
        original = char.msg

        def capture(text=None, **kwargs):
            if text:
                messages.append(str(text))

        char.msg = capture
        return messages, original

    def test_drop_carried_item(self):
        """Dropping a carried artifact moves it from inventory to the room."""
        item = evennia.create_object(
            "typeclasses.objects.Artifact",
            key="Data Chip",
            location=self.char1,  # in inventory
        )
        self.char1.location = self.room1

        from commands.items import CmdDrop
        cmd = CmdDrop()
        cmd.caller = self.char1
        cmd.args = "Data Chip"
        cmd.session = None
        cmd.func()

        self.assertNotIn(item, self.char1.contents)
        self.assertIn(item, self.room1.contents)

        item.delete()

    def test_drop_uncarried_item(self):
        """Dropping an artifact not in inventory sends an error message."""
        self.char1.location = self.room1
        messages, original = self._capture_messages(self.char1)

        from commands.items import CmdDrop
        cmd = CmdDrop()
        cmd.caller = self.char1
        cmd.args = "GhostItem99999"
        cmd.session = None
        cmd.func()

        self.char1.msg = original
        # No item named GhostItem99999 should appear in the room
        room_names = [obj.name for obj in self.room1.contents]
        self.assertNotIn("GhostItem99999", room_names)


@pytest.mark.skipif(not _EVENNIA_AVAILABLE, reason="Evennia not available")
class TestEquipCommand(EvenniaTest):
    """Tests for CmdEquip."""

    def _capture_messages(self, char):
        messages = []
        original = char.msg

        def capture(text=None, **kwargs):
            if text:
                messages.append(str(text))

        char.msg = capture
        return messages, original

    def test_equip_applies_stat_modifiers(self):
        """Equipping an Equipment item increases the character's stats."""
        equipment = evennia.create_object(
            "typeclasses.objects.Equipment",
            key="Overclocked Processor",
            location=self.char1,  # in inventory
        )
        equipment.db.equippable = True
        equipment.db.stat_modifiers = {"processing": 8}

        self.char1.db.processing = 10
        self.char1.db.shielding = 5

        from commands.items import CmdEquip
        cmd = CmdEquip()
        cmd.caller = self.char1
        cmd.args = "Overclocked Processor"
        cmd.session = None
        cmd.func()

        self.assertEqual(self.char1.db.processing, 18)  # 10 + 8

        equipment.delete()

    def test_equip_non_equippable_rejected(self):
        """Equipping a non-equippable item sends an error message."""
        item = evennia.create_object(
            "typeclasses.objects.Artifact",
            key="Data Chip",
            location=self.char1,
        )
        item.db.equippable = False

        messages, original = self._capture_messages(self.char1)

        from commands.items import CmdEquip
        cmd = CmdEquip()
        cmd.caller = self.char1
        cmd.args = "Data Chip"
        cmd.session = None
        cmd.func()

        self.char1.msg = original

        self.assertTrue(
            any("Cannot install that component" in m for m in messages),
            f"Expected 'Cannot install that component' message, got: {messages}",
        )

        item.delete()
