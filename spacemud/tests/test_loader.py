"""
Tests for world/loader.py — the JSON world loader.

Tests 1-3 cover _load_json in isolation using unittest.mock.patch
to avoid filesystem dependencies.

Tests 4-6 cover _load_rooms, _load_exits, and _load_artifacts by
mocking _load_json (to supply controlled data) and create_object
(to avoid needing a live Evennia database).
"""

import json
import tempfile
import os
from unittest.mock import MagicMock, patch, call

import pytest

from world.loader import _load_json, _load_rooms, _load_exits, _load_artifacts, DATA_DIR


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _mock_room(key):
    """Return a MagicMock that behaves like a minimal Evennia room."""
    room = MagicMock()
    room.key = key
    room.db = MagicMock()
    room.tags = MagicMock()
    return room


# ---------------------------------------------------------------------------
# _load_json
# ---------------------------------------------------------------------------


class TestLoadJson:
    def test_valid_file_returns_parsed_data(self):
        """_load_json with a valid JSON file returns the parsed content."""
        payload = [{"key": "Test Room", "zone": "alpha"}]

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", dir=DATA_DIR, delete=False
        ) as tmp:
            json.dump(payload, tmp)
            tmp_name = os.path.basename(tmp.name)

        try:
            result = _load_json(tmp_name)
            assert result == payload
        finally:
            os.unlink(os.path.join(DATA_DIR, tmp_name))

    def test_missing_file_raises_file_not_found(self):
        """_load_json with a non-existent file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError, match="no_such_file.json"):
            _load_json("no_such_file.json")

    def test_malformed_json_raises_value_error(self):
        """_load_json with invalid JSON raises ValueError."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", dir=DATA_DIR, delete=False
        ) as tmp:
            tmp.write("{bad json!!")
            tmp_name = os.path.basename(tmp.name)

        try:
            with pytest.raises(ValueError, match="Malformed JSON"):
                _load_json(tmp_name)
        finally:
            os.unlink(os.path.join(DATA_DIR, tmp_name))


# ---------------------------------------------------------------------------
# _load_rooms
# ---------------------------------------------------------------------------


class TestLoadRooms:
    @patch("world.loader.create_object")
    @patch("world.loader._load_json")
    def test_creates_rooms_with_zone_and_description(self, mock_json, mock_create):
        """_load_rooms creates rooms and sets zone + desc attributes."""
        mock_json.return_value = [
            {
                "key": "Main Corridor",
                "zone": "central_station",
                "desc": "A long corridor.",
                "tags": ["start"],
                "pvp_zone": False,
            },
            {
                "key": "Cargo Bay",
                "zone": "outer_zone",
                "desc": "Crates everywhere.",
                "tags": [],
                "pvp_zone": True,
            },
        ]

        room1 = _mock_room("Main Corridor")
        room2 = _mock_room("Cargo Bay")
        mock_create.side_effect = [room1, room2]

        rooms = _load_rooms()

        assert len(rooms) == 2
        assert "Main Corridor" in rooms
        assert "Cargo Bay" in rooms

        # Verify zone and desc were set
        assert room1.db.zone == "central_station"
        assert room1.db.desc == "A long corridor."
        assert room2.db.zone == "outer_zone"
        assert room2.db.desc == "Crates everywhere."

        # Verify tags were applied
        room1.tags.add.assert_called_once_with("start")


# ---------------------------------------------------------------------------
# _load_exits
# ---------------------------------------------------------------------------


class TestLoadExits:
    @patch("world.loader.create_object")
    @patch("world.loader._load_json")
    def test_connects_correct_rooms(self, mock_json, mock_create):
        """_load_exits creates exits linking the right source and destination."""
        mock_json.return_value = [
            {"from": "Room A", "to": "Room B", "direction": "north"},
            {"from": "Room B", "to": "Room A", "direction": "south"},
        ]

        room_a = _mock_room("Room A")
        room_b = _mock_room("Room B")
        rooms = {"Room A": room_a, "Room B": room_b}

        exit_mock = MagicMock()
        mock_create.return_value = exit_mock

        count = _load_exits(rooms)

        assert count == 2
        mock_create.assert_any_call(
            "evennia.objects.objects.DefaultExit",
            key="north",
            location=room_a,
            destination=room_b,
        )
        mock_create.assert_any_call(
            "evennia.objects.objects.DefaultExit",
            key="south",
            location=room_b,
            destination=room_a,
        )


# ---------------------------------------------------------------------------
# _load_artifacts
# ---------------------------------------------------------------------------


class TestLoadArtifacts:
    @patch("world.loader.create_object")
    @patch("world.loader._load_json")
    def test_creates_artifacts_with_stats_and_location(self, mock_json, mock_create):
        """_load_artifacts sets stat_modifiers, item_type, and location."""
        mock_json.return_value = [
            {
                "key": "Reinforced Plating",
                "typeclass": "typeclasses.objects.Equipment",
                "location": "Cargo Bay",
                "item_type": "component",
                "equippable": True,
                "stat_modifiers": {"shielding": 5},
                "desc": "Composite alloy plating.",
            },
            {
                "key": "Data Chip",
                "typeclass": "typeclasses.objects.Artifact",
                "location": "Data Core",
                "item_type": "quest",
                "equippable": False,
                "stat_modifiers": {},
                "desc": "Encrypted data chip.",
            },
        ]

        cargo = _mock_room("Cargo Bay")
        data_core = _mock_room("Data Core")
        rooms = {"Cargo Bay": cargo, "Data Core": data_core}

        art1 = MagicMock()
        art1.db = MagicMock()
        art2 = MagicMock()
        art2.db = MagicMock()
        mock_create.side_effect = [art1, art2]

        count = _load_artifacts(rooms)

        assert count == 2

        # First artifact — equipment with stat modifiers
        mock_create.assert_any_call(
            "typeclasses.objects.Equipment",
            key="Reinforced Plating",
            location=cargo,
        )
        assert art1.db.stat_modifiers == {"shielding": 5}
        assert art1.db.equippable is True
        assert art1.db.item_type == "component"

        # Second artifact — quest item, no stats
        mock_create.assert_any_call(
            "typeclasses.objects.Artifact",
            key="Data Chip",
            location=data_core,
        )
        assert art2.db.stat_modifiers == {}
        assert art2.db.equippable is False
        assert art2.db.item_type == "quest"
