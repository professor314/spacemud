"""
Tests for utils/validate_world.py.

Each check function is tested in isolation using unittest.mock.patch
to avoid needing a live Evennia database.

Covers:
- A valid world (no issues) passes all checks
- A broken exit (no destination) is detected
- An unreachable room is detected
- An NPC with None home_location is detected
- A mission with a non-existent giver NPC is detected
- A repairable object with missing required artifact is detected
"""

from unittest.mock import MagicMock, patch
import pytest


# ---------------------------------------------------------------------------
# Helpers to build mock Evennia objects
# ---------------------------------------------------------------------------


def _make_room(key, pk):
    room = MagicMock()
    room.key = key
    room.pk = pk
    room.exits = []
    return room


def _make_exit(key, location, destination):
    exit_obj = MagicMock()
    exit_obj.key = key
    exit_obj.location = location
    exit_obj.destination = destination
    if destination is not None:
        destination.pk  # ensure pk is accessible
    return exit_obj


def _make_npc(key, home_location):
    npc = MagicMock()
    npc.key = key
    npc.db = MagicMock()
    npc.db.home_location = home_location
    return npc


# ---------------------------------------------------------------------------
# check_exit_validity
# ---------------------------------------------------------------------------


class TestCheckExitValidity:
    def test_valid_exits_pass(self):
        """Exits with valid destinations produce no errors."""
        room_a = _make_room("Room A", 1)
        room_b = _make_room("Room B", 2)
        exit_obj = _make_exit("north", room_a, room_b)

        with patch("evennia.search_object", return_value=[exit_obj]):
            from utils.validate_world import check_exit_validity
            errors = check_exit_validity()

        assert errors == []

    def test_broken_exit_detected(self):
        """An exit with destination=None is reported as an error."""
        room_a = _make_room("Room A", 1)
        exit_obj = _make_exit("north", room_a, None)

        with patch("evennia.search_object", return_value=[exit_obj]):
            from utils.validate_world import check_exit_validity
            errors = check_exit_validity()

        assert len(errors) == 1
        assert "north" in errors[0]
        assert "no valid destination" in errors[0].lower()


# ---------------------------------------------------------------------------
# check_room_connectivity
# ---------------------------------------------------------------------------


class TestCheckRoomConnectivity:
    def test_valid_world_passes(self):
        """All rooms reachable from the start room produce no errors."""
        room_a = _make_room("Room A", 1)
        room_b = _make_room("Room B", 2)

        exit_ab = _make_exit("north", room_a, room_b)
        room_a.exits = [exit_ab]
        room_b.exits = []

        with patch("evennia.search_object", return_value=[room_a, room_b]):
            from utils.validate_world import check_room_connectivity
            errors = check_room_connectivity()

        assert errors == []

    def test_unreachable_room_detected(self):
        """A room with no exits connecting to it is reported."""
        room_a = _make_room("Room A", 1)
        room_b = _make_room("Room B", 2)
        room_c = _make_room("Isolated Room", 3)

        exit_ab = _make_exit("north", room_a, room_b)
        room_a.exits = [exit_ab]
        room_b.exits = []
        room_c.exits = []  # no way to reach room_c

        with patch("evennia.search_object", return_value=[room_a, room_b, room_c]):
            from utils.validate_world import check_room_connectivity
            errors = check_room_connectivity()

        assert len(errors) == 1
        assert "Isolated Room" in errors[0]


# ---------------------------------------------------------------------------
# check_npc_home_locations
# ---------------------------------------------------------------------------


class TestCheckNpcHomeLocations:
    def test_valid_npc_home_passes(self):
        """NPCs with valid home_location produce no errors."""
        room = _make_room("Main Corridor", 10)
        npc = _make_npc("Maintenance Unit 7", room)

        with patch("evennia.search_object", return_value=[npc]):
            from utils.validate_world import check_npc_home_locations
            errors = check_npc_home_locations()

        assert errors == []

    def test_missing_npc_home_detected(self):
        """An NPC with home_location=None is reported."""
        npc = _make_npc("Rogue NPC", None)

        with patch("evennia.search_object", return_value=[npc]):
            from utils.validate_world import check_npc_home_locations
            errors = check_npc_home_locations()

        assert len(errors) == 1
        assert "Rogue NPC" in errors[0]
        assert "home_location" in errors[0].lower()


# ---------------------------------------------------------------------------
# check_mission_integrity
# ---------------------------------------------------------------------------


class TestCheckMissionIntegrity:
    def test_valid_mission_passes(self):
        """A mission whose giver NPC exists produces no errors."""
        npc = _make_npc("Maintenance Unit 7", MagicMock())

        def mock_search(name, typeclass=None):
            if name == "Maintenance Unit 7":
                return [npc]
            if name == "Damaged Scout":
                return [_make_npc("Damaged Scout", MagicMock())]
            # Return a match for any artifact/room/hostile target
            return [MagicMock()]

        with patch("evennia.search_object", side_effect=mock_search):
            from utils.validate_world import check_mission_integrity
            errors = check_mission_integrity()

        assert errors == [], f"Unexpected errors: {errors}"

    def test_missing_mission_giver_detected(self):
        """A mission with a non-existent giver NPC is reported."""

        def mock_search(name, typeclass=None):
            # Giver NPC not found; other targets found
            if typeclass and "NPC" in typeclass:
                return []
            return [MagicMock()]

        with patch("evennia.search_object", side_effect=mock_search):
            from utils.validate_world import check_mission_integrity
            errors = check_mission_integrity()

        assert any("giver NPC" in e for e in errors), (
            f"Expected giver NPC error, got: {errors}"
        )


# ---------------------------------------------------------------------------
# check_repairable_objects
# ---------------------------------------------------------------------------


class TestCheckRepairableObjects:
    def test_valid_repairable_passes(self):
        """A repairable object whose required artifacts exist produces no errors."""
        repairable = MagicMock()
        repairable.key = "Emergency Lighting"
        repairable.db.repair_cost = {"Power Cell": 1}

        def mock_search(name=None, typeclass=None):
            if typeclass and "RepairableObject" in typeclass:
                return [repairable]
            # Power Cell exists
            return [MagicMock()]

        with patch("evennia.search_object", side_effect=mock_search):
            from utils.validate_world import check_repairable_objects
            errors = check_repairable_objects()

        assert errors == []

    def test_missing_artifact_detected(self):
        """A repairable object requiring a non-existent artifact is reported."""
        repairable = MagicMock()
        repairable.key = "Reactor Coupling"
        repairable.db.repair_cost = {"Nonexistent Part": 2}

        def mock_search(name=None, typeclass=None):
            if typeclass and "RepairableObject" in typeclass:
                return [repairable]
            # Artifact not found
            if name == "Nonexistent Part":
                return []
            return [MagicMock()]

        with patch("evennia.search_object", side_effect=mock_search):
            from utils.validate_world import check_repairable_objects
            errors = check_repairable_objects()

        assert len(errors) == 1
        assert "Nonexistent Part" in errors[0]
        assert "Reactor Coupling" in errors[0]
