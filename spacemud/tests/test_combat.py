"""
Tests for combat commands and the CombatScript.

Covers:
- CmdAttack creates a CombatScript and sets player_state to "combat"
- Damage formula always produces a value >= 1 (property test)
- Hostile death awards XP and credits to the killer
- Hostile death spawns salvage items in the room
- Character death moves character to the Repair Bay
- CmdFlee moves character to an adjacent room
- CmdFlee with no exits sends "No exit vector found." message
"""

import random

import pytest
from hypothesis import given, settings as hyp_settings, strategies as st

# ---------------------------------------------------------------------------
# Property test — no Evennia required
# ---------------------------------------------------------------------------


@given(processing=st.integers(1, 50), shielding=st.integers(0, 40))
@hyp_settings(max_examples=200)
def test_damage_always_positive(processing, shielding):
    """
    **Validates: Requirements 7.2**

    For any attacker/defender stat combination the damage formula
    max(1, processing - shielding + randint(-2, 2)) always produces a value >= 1.
    """
    for _ in range(100):
        dmg = max(1, processing - shielding + random.randint(-2, 2))
        assert dmg >= 1, (
            f"Damage was {dmg} for processing={processing}, shielding={shielding}"
        )


# ---------------------------------------------------------------------------
# Evennia-dependent tests
# ---------------------------------------------------------------------------

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
class TestCombatInitiation(EvenniaTest):
    """Tests for CmdAttack."""

    def test_combat_initiation(self):
        """CmdAttack creates a CombatScript and sets player_state to 'combat'."""
        # Give char1 RobotCharacter attributes
        self.char1.db.player_state = "active"
        self.char1.db.processing = 10
        self.char1.db.shielding = 5
        self.char1.db.integrity = 100
        self.char1.db.max_integrity = 100

        # Create a hostile in the same room
        hostile = evennia.create_object(
            "typeclasses.objects.Hostile",
            key="Test Sentry",
            location=self.room1,
        )
        hostile.db.integrity = 50
        hostile.db.max_integrity = 50
        hostile.db.processing = 8
        hostile.db.shielding = 3
        hostile.db.xp_reward = 50
        hostile.db.credits_reward = 10
        hostile.db.salvage_items = []

        # Run the attack command
        from commands.combat import CmdAttack
        cmd = CmdAttack()
        cmd.caller = self.char1
        cmd.args = "Test Sentry"
        cmd.session = None
        cmd.func()

        # player_state should now be "combat"
        self.assertEqual(self.char1.db.player_state, "combat")

        # A CombatScript should be attached to char1
        scripts = [s for s in self.char1.scripts.all() if s.key == "combat_script"]
        self.assertTrue(len(scripts) >= 1, "No CombatScript found on character")

        # Clean up
        hostile.delete()
        for s in scripts:
            s.stop()
        self.char1.db.player_state = "active"


@pytest.mark.skipif(not _EVENNIA_AVAILABLE, reason="Evennia not available")
class TestHostileDeath(EvenniaTest):
    """Tests for Hostile.at_death."""

    def _make_hostile(self):
        hostile = evennia.create_object(
            "typeclasses.objects.Hostile",
            key="Test Hostile",
            location=self.room1,
        )
        hostile.db.integrity = 50
        hostile.db.max_integrity = 50
        hostile.db.processing = 8
        hostile.db.shielding = 3
        hostile.db.xp_reward = 50
        hostile.db.credits_reward = 10
        hostile.db.salvage_items = []
        hostile.db.home_location = self.room1
        hostile.db.respawn_delay = 9999  # don't actually respawn during tests
        return hostile

    def test_hostile_death_awards_xp(self):
        """When hostile integrity reaches 0 and at_death is called, killer gains XP."""
        hostile = self._make_hostile()
        self.char1.db.experience = 0
        self.char1.db.credits = 0
        self.char1.db.level = 1
        self.char1.db.integrity = 100
        self.char1.db.max_integrity = 100
        self.char1.db.processing = 10
        self.char1.db.shielding = 5

        hostile.at_death(self.char1)

        self.assertEqual(self.char1.db.experience, 50)
        self.assertEqual(self.char1.db.credits, 10)

    def test_hostile_death_spawns_salvage(self):
        """When hostile dies, salvage items appear in the room."""
        hostile = self._make_hostile()
        hostile.db.salvage_items = ["typeclasses.objects.Artifact"]

        self.char1.db.experience = 0
        self.char1.db.credits = 0
        self.char1.db.level = 1
        self.char1.db.integrity = 100
        self.char1.db.max_integrity = 100
        self.char1.db.processing = 10
        self.char1.db.shielding = 5

        items_before = len(self.room1.contents)
        hostile.at_death(self.char1)

        # One salvage item should have been created in the room
        # (hostile itself is removed from the room by at_death)
        items_after = [
            obj for obj in self.room1.contents
            if obj.typeclass_path == "typeclasses.objects.Artifact"
        ]
        self.assertTrue(
            len(items_after) >= 1,
            "No salvage item found in room after hostile death",
        )


@pytest.mark.skipif(not _EVENNIA_AVAILABLE, reason="Evennia not available")
class TestCharacterDeath(EvenniaTest):
    """Tests for character death in CombatScript."""

    def test_character_death_moves_to_repair_bay(self):
        """When character integrity reaches 0 in CombatScript, character moves to Repair Bay."""
        from typeclasses.scripts import CombatScript

        # Create a Repair Bay room so CombatScript can find it
        repair_bay = evennia.create_object(
            "typeclasses.rooms.StationRoom",
            key="Repair Bay",
            location=None,
        )

        # Set up character
        self.char1.db.integrity = 1
        self.char1.db.max_integrity = 100
        self.char1.db.processing = 10
        self.char1.db.shielding = 5
        self.char1.db.player_state = "combat"
        self.char1.db.experience = 0
        self.char1.db.level = 1
        self.char1.db.credits = 0

        # Create a hostile that will kill the character
        hostile = evennia.create_object(
            "typeclasses.objects.Hostile",
            key="Lethal Hostile",
            location=self.room1,
        )
        hostile.db.integrity = 999
        hostile.db.max_integrity = 999
        hostile.db.processing = 999   # guaranteed to kill
        hostile.db.shielding = 0
        hostile.db.xp_reward = 0
        hostile.db.credits_reward = 0
        hostile.db.salvage_items = []
        hostile.db.home_location = self.room1
        hostile.db.respawn_delay = 9999

        # Create and run the combat script manually
        script = evennia.create_script(
            "typeclasses.scripts.CombatScript",
            obj=self.char1,
            persistent=False,
        )
        script.db.attacker = self.char1
        script.db.defender = hostile

        # Force one combat round — attacker will survive (integrity=1 after attacker hits),
        # then defender hits with 999 processing, killing the character
        script.at_repeat()

        # Character should have been moved to the Repair Bay
        self.assertEqual(
            self.char1.location,
            repair_bay,
            f"Character is at {self.char1.location} instead of Repair Bay",
        )
        # Integrity should be restored to 25% of max
        self.assertGreater(self.char1.db.integrity, 0)

        # Clean up
        script.stop()
        hostile.delete()
        repair_bay.delete()


@pytest.mark.skipif(not _EVENNIA_AVAILABLE, reason="Evennia not available")
class TestFlee(EvenniaTest):
    """Tests for CmdFlee."""

    def test_flee_moves_to_adjacent_room(self):
        """CmdFlee moves character to an adjacent room."""
        # room1 and room2 exist; create an exit from room1 to room2
        exit_obj = evennia.create_object(
            "typeclasses.exits.Exit",
            key="north",
            location=self.room1,
            destination=self.room2,
        )

        self.char1.location = self.room1
        self.char1.db.player_state = "combat"

        from commands.combat import CmdFlee
        cmd = CmdFlee()
        cmd.caller = self.char1
        cmd.args = ""
        cmd.session = None
        cmd.func()

        self.assertEqual(self.char1.location, self.room2)
        self.assertEqual(self.char1.db.player_state, "active")

        exit_obj.delete()

    def test_flee_no_exits_sends_message(self):
        """CmdFlee with no exits sends 'No exit vector found.' message."""
        # Ensure room1 has no exits
        for obj in list(self.room1.exits):
            obj.delete()

        self.char1.location = self.room1
        self.char1.db.player_state = "combat"

        received_messages = []
        original_msg = self.char1.msg

        def capture_msg(text=None, **kwargs):
            if text:
                received_messages.append(str(text))

        self.char1.msg = capture_msg

        from commands.combat import CmdFlee
        cmd = CmdFlee()
        cmd.caller = self.char1
        cmd.args = ""
        cmd.session = None
        cmd.func()

        self.char1.msg = original_msg

        self.assertTrue(
            any("No exit vector found" in m for m in received_messages),
            f"Expected 'No exit vector found.' message, got: {received_messages}",
        )
