"""
Tests for the chassis system.

Covers:
- install_chassis applies stat modifiers correctly
- install_chassis persists chassis ID on db
- second chassis install is rejected
- CmdChassisInfo displays chassis name and passive description
- CmdChassisInfo with no chassis shows bare circuit board message
"""

import pytest


# ---------------------------------------------------------------------------
# Fake character — mirrors the _FakeChar pattern from test_missions.py
# ---------------------------------------------------------------------------


class _FakeChar:
    """Minimal stand-in for a RobotCharacter used in pure-logic tests."""

    def __init__(self):
        self._messages = []
        self.name = "TestBot"
        self._db = {
            "level": 1,
            "experience": 0,
            "integrity": 100,
            "max_integrity": 100,
            "power": 50,
            "max_power": 50,
            "processing": 10,
            "shielding": 5,
            "repair_level": 1,
            "credits": 0,
            "chassis": None,
            "profession": None,
            "skills": [],
            "skill_cooldowns": {},
        }

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

    # Bind the real install_chassis logic from the typeclass
    def install_chassis(self, chassis_id):
        if self.db.chassis:
            self.msg("Chassis already installed.")
            return False
        from world.chassis import CHASSIS

        chassis = CHASSIS.get(chassis_id)
        if not chassis:
            self.msg("Unknown chassis type.")
            return False
        for stat, value in chassis["stat_modifiers"].items():
            current = getattr(self.db, stat, 0)
            setattr(self.db, stat, current + value)
        self.db.chassis = chassis_id
        self.msg(f"Chassis installed: {chassis['name']}. Systems recalibrating.")
        return True


# ---------------------------------------------------------------------------
# Tests 1-3: install_chassis logic (no Evennia needed)
# ---------------------------------------------------------------------------


def test_install_chassis_applies_modifiers():
    """Installing 'scout' chassis increases processing by 3, decreases shielding by 1, increases max_power by 10."""
    char = _FakeChar()
    orig_processing = char.db.processing
    orig_shielding = char.db.shielding
    orig_max_power = char.db.max_power

    result = char.install_chassis("scout")

    assert result is True
    assert char.db.processing == orig_processing + 3
    assert char.db.shielding == orig_shielding - 1
    assert char.db.max_power == orig_max_power + 10


def test_install_chassis_sets_db_permanently():
    """After install, db.chassis equals the chassis ID."""
    char = _FakeChar()
    assert char.db.chassis is None

    char.install_chassis("scout")

    assert char.db.chassis == "scout"


def test_second_install_rejected():
    """Installing a chassis when one is already set returns False and doesn't change stats."""
    char = _FakeChar()
    char.install_chassis("scout")

    processing_after_first = char.db.processing
    shielding_after_first = char.db.shielding
    max_power_after_first = char.db.max_power

    result = char.install_chassis("heavy")

    assert result is False
    assert char.db.chassis == "scout"
    assert char.db.processing == processing_after_first
    assert char.db.shielding == shielding_after_first
    assert char.db.max_power == max_power_after_first


# ---------------------------------------------------------------------------
# Tests 4-5: CmdChassisInfo display (uses _FakeChar + command func)
# ---------------------------------------------------------------------------


class _FakeCaller(_FakeChar):
    """Extends _FakeChar with a location attribute for command tests."""

    def __init__(self):
        super().__init__()
        self.location = None


def _run_chassis_cmd(caller):
    """Instantiate CmdChassisInfo and execute it against the given caller."""
    from commands.chassis import CmdChassisInfo

    cmd = CmdChassisInfo()
    cmd.caller = caller
    cmd.args = ""
    cmd.cmdstring = "chassis"
    cmd.raw_string = "chassis"
    cmd.func()
    return caller._messages


def test_chassis_command_shows_info():
    """CmdChassisInfo displays chassis name and passive description."""
    caller = _FakeCaller()
    caller.install_chassis("scout")
    caller._messages.clear()

    messages = _run_chassis_cmd(caller)

    combined = "\n".join(messages)
    assert "Scout Unit" in combined
    assert "Sensor range extended" in combined


def test_no_chassis_shows_bare_circuit_board():
    """CmdChassisInfo with no chassis shows 'bare circuit board'."""
    caller = _FakeCaller()

    messages = _run_chassis_cmd(caller)

    combined = "\n".join(messages)
    assert "bare circuit board" in combined.lower()
