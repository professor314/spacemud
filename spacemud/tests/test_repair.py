"""
Tests for the repair system.

Covers:
- Repair with sufficient level and components succeeds
- Repair with insufficient level rejected
- Repair with missing components rejected
- Repair fires repair_completed event
- Already-repaired object rejected
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
class TestRepairCommand(EvenniaTest):
    """Tests for CmdRepair."""

    def _capture_messages(self, char):
        """Monkey-patch char.msg to capture sent messages."""
        messages = []
        original = char.msg

        def capture(text=None, **kwargs):
            if text:
                messages.append(str(text))

        char.msg = capture
        return messages, original

    def _setup_char(self):
        """Give char1 the required RobotCharacter attributes."""
        self.char1.db.repair_level = 2
        self.char1.db.integrity = 100
        self.char1.db.max_integrity = 100
        self.char1.db.power = 50
        self.char1.db.max_power = 50
        self.char1.db.processing = 10
        self.char1.db.shielding = 5
        self.char1.db.player_state = "active"

    def test_repair_succeeds_with_sufficient_level_and_components(self):
        """Repair with sufficient level and components marks object repaired and consumes components."""
        self._setup_char()
        self.char1.location = self.room1

        # Create a repairable object in the room
        repairable = evennia.create_object(
            "typeclasses.objects.RepairableObject",
            key="Emergency Lighting",
            location=self.room1,
        )
        repairable.db.repaired = False
        repairable.db.repair_level_required = 1
        repairable.db.repair_cost = {"Power Cell": 1}
        repairable.db.power_cost = 0
        repairable.db.on_repair_message = "Lights flicker on."

        # Give the character the required component
        component = evennia.create_object(
            "typeclasses.objects.Artifact",
            key="Power Cell",
            location=self.char1,
        )

        from commands.general import CmdRepair
        cmd = CmdRepair()
        cmd.caller = self.char1
        cmd.args = "Emergency Lighting"
        cmd.session = None
        cmd.func()

        # Object should be marked as repaired
        self.assertTrue(repairable.db.repaired)

        # Component should have been consumed (deleted)
        self.assertNotIn(component, self.char1.contents)

        # Clean up
        repairable.delete()

    def test_repair_insufficient_level_rejected(self):
        """Repair with insufficient repair level sends error message."""
        self._setup_char()
        self.char1.db.repair_level = 1  # below required
        self.char1.location = self.room1

        repairable = evennia.create_object(
            "typeclasses.objects.RepairableObject",
            key="Reactor Coupling",
            location=self.room1,
        )
        repairable.db.repaired = False
        repairable.db.repair_level_required = 5
        repairable.db.repair_cost = {}

        messages, original = self._capture_messages(self.char1)

        from commands.general import CmdRepair
        cmd = CmdRepair()
        cmd.caller = self.char1
        cmd.args = "Reactor Coupling"
        cmd.session = None
        cmd.func()

        self.char1.msg = original

        self.assertFalse(repairable.db.repaired)
        self.assertTrue(
            any("Repair level insufficient" in m for m in messages),
            f"Expected 'Repair level insufficient' message, got: {messages}",
        )

        repairable.delete()

    def test_repair_missing_components_rejected(self):
        """Repair with missing components sends error message."""
        self._setup_char()
        self.char1.location = self.room1

        repairable = evennia.create_object(
            "typeclasses.objects.RepairableObject",
            key="Emergency Lighting",
            location=self.room1,
        )
        repairable.db.repaired = False
        repairable.db.repair_level_required = 1
        repairable.db.repair_cost = {"Power Cell": 2}

        # Character has no Power Cells
        messages, original = self._capture_messages(self.char1)

        from commands.general import CmdRepair
        cmd = CmdRepair()
        cmd.caller = self.char1
        cmd.args = "Emergency Lighting"
        cmd.session = None
        cmd.func()

        self.char1.msg = original

        self.assertFalse(repairable.db.repaired)
        self.assertTrue(
            any("Insufficient components" in m for m in messages),
            f"Expected 'Insufficient components' message, got: {messages}",
        )

        repairable.delete()

    def test_repair_fires_event(self):
        """Repair fires the repair_completed event."""
        self._setup_char()
        self.char1.location = self.room1

        repairable = evennia.create_object(
            "typeclasses.objects.RepairableObject",
            key="Emergency Lighting",
            location=self.room1,
        )
        repairable.db.repaired = False
        repairable.db.repair_level_required = 1
        repairable.db.repair_cost = {}
        repairable.db.power_cost = 0
        repairable.db.on_repair_message = "Lights restored."

        # Register a handler to capture the event
        events_fired = []
        from utils.events import on
        on("repair_completed", lambda **kwargs: events_fired.append(kwargs))

        from commands.general import CmdRepair
        cmd = CmdRepair()
        cmd.caller = self.char1
        cmd.args = "Emergency Lighting"
        cmd.session = None
        cmd.func()

        self.assertTrue(
            len(events_fired) >= 1,
            "Expected repair_completed event to fire",
        )
        self.assertEqual(events_fired[0]["target"], repairable)
        self.assertEqual(events_fired[0]["character"], self.char1)

        repairable.delete()

    def test_already_repaired_rejected(self):
        """Attempting to repair an already-repaired object sends error message."""
        self._setup_char()
        self.char1.location = self.room1

        repairable = evennia.create_object(
            "typeclasses.objects.RepairableObject",
            key="Emergency Lighting",
            location=self.room1,
        )
        repairable.db.repaired = True
        repairable.db.repair_level_required = 1
        repairable.db.repair_cost = {}

        messages, original = self._capture_messages(self.char1)

        from commands.general import CmdRepair
        cmd = CmdRepair()
        cmd.caller = self.char1
        cmd.args = "Emergency Lighting"
        cmd.session = None
        cmd.func()

        self.char1.msg = original

        self.assertTrue(
            any("Already repaired" in m for m in messages),
            f"Expected 'Already repaired' message, got: {messages}",
        )

        repairable.delete()
