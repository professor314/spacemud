"""
Tests for the mission system.

Covers:
- accept_mission adds mission to character's mission_log
- on_artifact_collected increments collect objective count
- all objectives complete triggers a notification message
- try_complete_mission grants XP and credits
- accepting the same mission twice is rejected
- completing with unfinished objectives is rejected
- objective count never decreases (property test)
"""

import copy
import pytest
from hypothesis import given, settings as hyp_settings, strategies as st

# ---------------------------------------------------------------------------
# Property test — no Evennia required
# ---------------------------------------------------------------------------


class _FakeChar:
    """Minimal stand-in for a character used in pure-logic property tests."""

    def __init__(self):
        self._messages = []
        self.name = "TestChar"
        self._db = {
            "mission_log": {},
            "experience": 0,
            "credits": 0,
            "level": 1,
            "integrity": 100,
            "max_integrity": 100,
            "processing": 10,
            "shielding": 5,
        }

    # Simulate Evennia's db attribute handler
    class _DB:
        def __init__(self, store):
            object.__setattr__(self, "_store", store)

        def __getattr__(self, name):
            return object.__getattribute__(self, "_store").get(name)

        def __setattr__(self, name, value):
            object.__getattribute__(self, "_store")[name] = value

    @property
    def db(self):
        return self._DB(self._db)

    def msg(self, text=None, **kwargs):
        if text:
            self._messages.append(str(text))

    def award_xp(self, amount):
        self._db["experience"] = (self._db.get("experience") or 0) + amount


class _FakeItem:
    def __init__(self, name):
        self.name = name


@given(collect_count=st.integers(min_value=0, max_value=50))
@hyp_settings(max_examples=100)
def test_objective_count_never_decreases(collect_count):
    """
    **Validates: Requirements 8.4, 16.8**

    Firing on_artifact_collected events many times never decreases the
    objective's current count.
    """
    from utils.missions import accept_mission, on_artifact_collected

    char = _FakeChar()
    # Accept the salvage_run mission (collect-based)
    accept_mission(char, "salvage_run")

    item = _FakeItem("Circuit Component")

    prev_count = 0
    for _ in range(collect_count):
        on_artifact_collected(character=char, item=item)
        log = char.db.mission_log or {}
        entry = log.get("salvage_run", {})
        objectives = entry.get("objectives", [])
        if objectives:
            current = objectives[0].get("current", 0)
            assert current >= prev_count, (
                f"Objective count decreased from {prev_count} to {current}"
            )
            prev_count = current


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


def _setup_char(char):
    """Give a test character the required RobotCharacter attributes."""
    char.db.mission_log = {}
    char.db.experience = 0
    char.db.credits = 0
    char.db.level = 1
    char.db.integrity = 100
    char.db.max_integrity = 100
    char.db.processing = 10
    char.db.shielding = 5


@pytest.mark.skipif(not _EVENNIA_AVAILABLE, reason="Evennia not available")
class TestAcceptMission(EvenniaTest):
    """Tests for accept_mission."""

    def test_accept_adds_to_log(self):
        """Accepting a mission adds it to the character's mission_log."""
        _setup_char(self.char1)

        from utils.missions import accept_mission
        accept_mission(self.char1, "salvage_run")

        log = self.char1.db.mission_log
        self.assertIn("salvage_run", log)
        self.assertEqual(log["salvage_run"]["state"], "in_progress")

    def test_duplicate_accept_rejected(self):
        """Accepting the same mission twice is rejected."""
        _setup_char(self.char1)

        from utils.missions import accept_mission
        accept_mission(self.char1, "salvage_run")

        messages = []
        original_msg = self.char1.msg

        def capture(text=None, **kwargs):
            if text:
                messages.append(str(text))

        self.char1.msg = capture
        accept_mission(self.char1, "salvage_run")
        self.char1.msg = original_msg

        self.assertTrue(
            any("already" in m.lower() for m in messages),
            f"Expected duplicate-rejection message, got: {messages}",
        )


@pytest.mark.skipif(not _EVENNIA_AVAILABLE, reason="Evennia not available")
class TestCollectEvent(EvenniaTest):
    """Tests for on_artifact_collected."""

    def test_collect_event_increments_objective(self):
        """on_artifact_collected increments the collect objective count."""
        _setup_char(self.char1)

        from utils.missions import accept_mission, on_artifact_collected
        accept_mission(self.char1, "salvage_run")

        item = evennia.create_object(
            "typeclasses.objects.Artifact",
            key="Circuit Component",
            location=self.room1,
        )

        on_artifact_collected(character=self.char1, item=item)

        log = self.char1.db.mission_log
        objectives = log["salvage_run"]["objectives"]
        self.assertEqual(objectives[0]["current"], 1)

        item.delete()

    def test_all_objectives_complete_triggers_notification(self):
        """When all objectives are done, the character gets a notification."""
        _setup_char(self.char1)

        from utils.missions import accept_mission, on_artifact_collected
        accept_mission(self.char1, "salvage_run")

        messages = []
        original_msg = self.char1.msg

        def capture(text=None, **kwargs):
            if text:
                messages.append(str(text))

        self.char1.msg = capture

        item = evennia.create_object(
            "typeclasses.objects.Artifact",
            key="Circuit Component",
            location=self.room1,
        )

        # Collect 2 components to complete the objective
        for _ in range(2):
            on_artifact_collected(character=self.char1, item=item)

        self.char1.msg = original_msg

        self.assertTrue(
            any("all objectives complete" in m.lower() for m in messages),
            f"Expected completion notification, got: {messages}",
        )

        item.delete()


@pytest.mark.skipif(not _EVENNIA_AVAILABLE, reason="Evennia not available")
class TestCompleteMission(EvenniaTest):
    """Tests for try_complete_mission."""

    def test_complete_grants_rewards(self):
        """try_complete_mission grants XP and credits when objectives are done."""
        _setup_char(self.char1)
        self.char1.location = self.room1

        from utils.missions import accept_mission, on_artifact_collected, try_complete_mission

        accept_mission(self.char1, "salvage_run")

        # Create and collect 2 circuit components
        item = evennia.create_object(
            "typeclasses.objects.Artifact",
            key="Circuit Component",
            location=self.room1,
        )

        for _ in range(2):
            on_artifact_collected(character=self.char1, item=item)

        # Place the mission giver NPC in the same room
        npc = evennia.create_object(
            "typeclasses.objects.NPC",
            key="Damaged Scout",
            location=self.room1,
        )

        xp_before = self.char1.db.experience
        credits_before = self.char1.db.credits or 0

        try_complete_mission(self.char1, "Salvage Run")

        self.assertGreater(self.char1.db.experience, xp_before)
        self.assertGreater(self.char1.db.credits, credits_before)

        log = self.char1.db.mission_log
        self.assertEqual(log["salvage_run"]["state"], "completed")

        item.delete()
        npc.delete()

    def test_complete_with_incomplete_objectives_rejected(self):
        """Completing a mission with unfinished objectives is rejected."""
        _setup_char(self.char1)
        self.char1.location = self.room1

        from utils.missions import accept_mission, try_complete_mission

        accept_mission(self.char1, "salvage_run")

        # Place the mission giver NPC in the same room
        npc = evennia.create_object(
            "typeclasses.objects.NPC",
            key="Damaged Scout",
            location=self.room1,
        )

        messages = []
        original_msg = self.char1.msg

        def capture(text=None, **kwargs):
            if text:
                messages.append(str(text))

        self.char1.msg = capture
        try_complete_mission(self.char1, "Salvage Run")
        self.char1.msg = original_msg

        # Mission should still be in_progress
        log = self.char1.db.mission_log
        self.assertEqual(log["salvage_run"]["state"], "in_progress")

        self.assertTrue(
            any("incomplete" in m.lower() for m in messages),
            f"Expected incomplete-objectives message, got: {messages}",
        )

        npc.delete()
