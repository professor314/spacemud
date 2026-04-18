"""
Tests for the skills system.

Covers:
- Generic skills usable by all characters
- Profession skills rejected if not unlocked
- Cooldown prevents immediate reuse
- Insufficient power rejected
- Heal effect restores integrity capped at max
- Bonus damage applied by quick_scan
- Restore power effect from signal_boost
- CmdSkills lists available generic skills
"""

import time

import pytest

from utils.skills import (
    apply_skill_effect,
    is_skill_ready,
    set_cooldown,
    remaining_cooldown,
)
from world.skills import SKILLS


# ---------------------------------------------------------------------------
# Fake character — mirrors the _FakeChar pattern from test_chassis.py
# ---------------------------------------------------------------------------


class _FakeScripts:
    """Minimal stand-in for character.scripts."""

    def all(self):
        return []


class _FakeChar:
    """Minimal stand-in for a RobotCharacter used in pure-logic tests."""

    def __init__(self):
        self._messages = []
        self.name = "TestBot"
        self.scripts = _FakeScripts()
        self._db = {
            "power": 50,
            "max_power": 50,
            "integrity": 100,
            "max_integrity": 100,
            "processing": 10,
            "shielding": 5,
            "skills": [],
            "skill_cooldowns": {},
            "bonus_damage": 0,
            "player_state": "active",
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


class _FakeCaller(_FakeChar):
    """Extends _FakeChar with a location attribute for command tests."""

    def __init__(self):
        super().__init__()
        self.location = None


# ---------------------------------------------------------------------------
# Helper to run a command against a fake caller
# ---------------------------------------------------------------------------


def _run_use_cmd(caller, args):
    """Instantiate CmdUse and execute it against the given caller."""
    from commands.skills import CmdUse

    cmd = CmdUse()
    cmd.caller = caller
    cmd.args = args
    cmd.cmdstring = "use"
    cmd.raw_string = f"use {args}"
    cmd.func()
    return caller._messages


def _run_skills_cmd(caller):
    """Instantiate CmdSkills and execute it against the given caller."""
    from commands.skills import CmdSkills

    cmd = CmdSkills()
    cmd.caller = caller
    cmd.args = ""
    cmd.cmdstring = "skills"
    cmd.raw_string = "skills"
    cmd.func()
    return caller._messages


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_generic_skill_usable_by_all():
    """quick_scan works without any profession skills unlocked."""
    caller = _FakeCaller()
    # db.skills is empty — no profession skills unlocked
    assert caller.db.skills == []

    messages = _run_use_cmd(caller, " quick scan")

    combined = "\n".join(messages)
    # quick_scan has effect "bonus_damage" — should see the boost message
    assert "boosted" in combined.lower() or "bonus" in combined.lower()


def test_profession_skill_rejected_if_not_unlocked():
    """upload_virus fails if not in db.skills."""
    caller = _FakeCaller()
    assert caller.db.skills == []

    messages = _run_use_cmd(caller, " upload virus")

    combined = "\n".join(messages)
    assert "not unlocked" in combined.lower()


def test_cooldown_prevents_reuse():
    """Using a skill then immediately trying again fails with cooldown message."""
    caller = _FakeCaller()

    # Use quick_scan once — should succeed
    _run_use_cmd(caller, " quick scan")
    caller._messages.clear()

    # Immediately try again — should be on cooldown
    messages = _run_use_cmd(caller, " quick scan")

    combined = "\n".join(messages)
    assert "cooldown" in combined.lower()


def test_insufficient_power_rejected():
    """Using a skill with power below cost fails."""
    caller = _FakeCaller()
    # quick_scan costs 10 power — set power to 0
    caller._db["power"] = 0

    messages = _run_use_cmd(caller, " quick scan")

    combined = "\n".join(messages)
    assert "insufficient power" in combined.lower()


def test_heal_restores_integrity():
    """emergency_patch restores integrity capped at max."""
    char = _FakeChar()
    char._db["integrity"] = 60
    char._db["max_integrity"] = 100

    skill = SKILLS["emergency_patch"]
    apply_skill_effect(char, skill)

    # 60 + 30 = 90, which is under max 100
    assert char.db.integrity == 90

    # Now test capping: set integrity to 85, heal 30 should cap at 100
    char._db["integrity"] = 85
    apply_skill_effect(char, skill)
    assert char.db.integrity == 100


def test_bonus_damage_applied():
    """quick_scan sets db.bonus_damage to 5."""
    char = _FakeChar()
    assert char.db.bonus_damage == 0

    skill = SKILLS["quick_scan"]
    apply_skill_effect(char, skill)

    assert char.db.bonus_damage == 5


def test_restore_power_effect():
    """signal_boost restores 10 power."""
    char = _FakeChar()
    char._db["power"] = 30
    char._db["max_power"] = 50

    skill = SKILLS["signal_boost"]
    apply_skill_effect(char, skill)

    assert char.db.power == 40


def test_skills_command_lists_available():
    """CmdSkills shows generic skills."""
    caller = _FakeCaller()

    messages = _run_skills_cmd(caller)

    combined = "\n".join(messages)
    # Should list generic skills like Quick Scan and Emergency Reboot
    assert "Quick Scan" in combined
    assert "Emergency Reboot" in combined
    # Should NOT list profession-locked skills since none are unlocked
    assert "Upload Virus" not in combined
