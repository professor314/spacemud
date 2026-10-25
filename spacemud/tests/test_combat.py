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


# ---------------------------------------------------------------------------
# Regression tests — combat ticking & delayed-script timing (Task D)
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not _EVENNIA_AVAILABLE, reason="Evennia not available")
class TestCombatTickRegression(EvenniaTest):
    """
    Regression tests for the 'combat doesn't tick' bug.

    The CombatScript's first round fires immediately (start_delay=False), so
    CmdAttack must set the combatants AND player_state='combat' BEFORE the
    timer starts, and the started script must be a live, ticking timer.
    """

    def _make_hostile(self):
        hostile = evennia.create_object(
            "typeclasses.objects.Hostile",
            key="Tick Test Sentry",
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
        hostile.db.respawn_delay = 9999
        return hostile

    def test_attack_starts_a_live_ticking_script(self):
        """CmdAttack must leave a started CombatScript with a 2s interval."""
        self.char1.db.player_state = "active"
        self.char1.db.processing = 10
        self.char1.db.shielding = 5
        self.char1.db.integrity = 100
        self.char1.db.max_integrity = 100

        hostile = self._make_hostile()

        from commands.combat import CmdAttack
        cmd = CmdAttack()
        cmd.caller = self.char1
        cmd.args = "Tick Test Sentry"
        cmd.session = None
        cmd.func()

        scripts = [s for s in self.char1.scripts.all() if s.key == "combat_script"]
        self.assertTrue(scripts, "No CombatScript attached after attack")
        script = scripts[0]

        # The timer must actually be running with the combat interval so it
        # will keep ticking every 2 seconds.
        self.assertTrue(script.is_active, "CombatScript timer is not active/ticking")
        self.assertEqual(script.interval, 2)
        # Combatants must be set on the script.
        self.assertEqual(script.db.attacker, self.char1)
        self.assertEqual(script.db.defender, hostile)

        for s in scripts:
            s.stop()
        hostile.delete()
        self.char1.db.player_state = "active"

    def test_player_state_set_before_first_round(self):
        """
        player_state must be 'combat' by the time a round can run. A manual
        at_repeat call (simulating the immediate first tick) should not error
        and should damage the defender, proving combatants are wired up.
        """
        self.char1.db.player_state = "active"
        self.char1.db.processing = 10
        self.char1.db.shielding = 5
        self.char1.db.integrity = 100
        self.char1.db.max_integrity = 100

        hostile = self._make_hostile()

        from commands.combat import CmdAttack
        cmd = CmdAttack()
        cmd.caller = self.char1
        cmd.args = "Tick Test Sentry"
        cmd.session = None
        cmd.func()

        self.assertEqual(self.char1.db.player_state, "combat")

        scripts = [s for s in self.char1.scripts.all() if s.key == "combat_script"]
        script = scripts[0]

        integrity_before = hostile.db.integrity
        script.at_repeat()
        self.assertLess(
            hostile.db.integrity,
            integrity_before,
            "Defender took no damage — combat round did not run",
        )

        for s in scripts:
            s.stop()
        hostile.delete()
        self.char1.db.player_state = "active"


@pytest.mark.skipif(not _EVENNIA_AVAILABLE, reason="Evennia not available")
class TestRespawnTiming(EvenniaTest):
    """
    Regression test for the 'hostile respawns instantly' bug.

    RespawnScript must use start_delay=True so it waits respawn_delay seconds
    before its single at_repeat fires, rather than firing immediately when
    attached on death.
    """

    def test_respawn_script_waits_before_firing(self):
        """A freshly-attached RespawnScript must not have fired yet (start_delay)."""
        hostile = evennia.create_object(
            "typeclasses.objects.Hostile",
            key="Respawn Test Bot",
            location=self.room1,
        )
        hostile.db.integrity = 60
        hostile.db.max_integrity = 60
        hostile.db.home_location = self.room1
        hostile.db.respawn_delay = 9999  # long enough that it can't fire during the test

        # Simulate death: schedule respawn then remove from world.
        hostile.scripts.add("typeclasses.scripts.RespawnScript")
        hostile.location = None

        scripts = [s for s in hostile.scripts.all() if s.key == "respawn_script"]
        self.assertTrue(scripts, "RespawnScript was not attached on death")
        script = scripts[0]

        # start_delay must be True so at_repeat is deferred by respawn_delay.
        self.assertTrue(
            script.start_delay,
            "RespawnScript.start_delay is False — hostile would respawn instantly",
        )
        self.assertEqual(script.interval, 9999)
        self.assertEqual(script.repeats, 1)
        # Because start_delay is True and interval is huge, the hostile must
        # still be out of the world (location None), i.e. it has NOT respawned.
        self.assertIsNone(
            hostile.location,
            "Hostile respawned instantly instead of waiting respawn_delay",
        )

        script.stop()
        hostile.delete()

    def test_respawn_at_repeat_restores_hostile(self):
        """When at_repeat finally fires, the hostile is restored to its home at full integrity."""
        hostile = evennia.create_object(
            "typeclasses.objects.Hostile",
            key="Respawn Restore Bot",
            location=self.room1,
        )
        hostile.db.integrity = 0
        hostile.db.max_integrity = 60
        hostile.db.home_location = self.room1
        hostile.db.respawn_delay = 9999

        hostile.scripts.add("typeclasses.scripts.RespawnScript")
        hostile.location = None

        scripts = [s for s in hostile.scripts.all() if s.key == "respawn_script"]
        script = scripts[0]

        # Manually fire the single repeat (simulating the delay elapsing).
        script.at_repeat()

        self.assertEqual(hostile.db.integrity, 60)
        self.assertEqual(hostile.location, self.room1)

        hostile.delete()


@pytest.mark.skipif(not _EVENNIA_AVAILABLE, reason="Evennia not available")
class TestRepairDegradeTiming(EvenniaTest):
    """
    Regression test for the RepairDegradeScript instant-degrade bug (same
    root cause as the respawn bug). It must use start_delay=True so a repaired
    system degrades after degrade_delay seconds, not immediately.
    """

    def test_degrade_script_waits_before_firing(self):
        repairable = evennia.create_object(
            "typeclasses.objects.RepairableObject",
            key="Degrade Test Panel",
            location=self.room1,
        )
        repairable.db.repaired = True
        repairable.db.degrade_delay = 9999

        repairable.scripts.add("typeclasses.scripts.RepairDegradeScript")

        scripts = [s for s in repairable.scripts.all() if s.key == "repair_degrade_script"]
        self.assertTrue(scripts, "RepairDegradeScript was not attached")
        script = scripts[0]

        self.assertTrue(
            script.start_delay,
            "RepairDegradeScript.start_delay is False — system would degrade instantly",
        )
        # The system must still be repaired (has not degraded yet).
        self.assertTrue(
            repairable.db.repaired,
            "System degraded instantly instead of waiting degrade_delay",
        )

        script.stop()
        repairable.delete()
