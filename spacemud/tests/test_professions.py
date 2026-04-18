"""
Tests for the professions system.

Covers:
- install_profession succeeds with chassis + level >= 3
- install_profession rejected without chassis
- install_profession rejected below level 3
- second profession install rejected
- level-up uses profession growth table
- skills unlock at correct levels
"""

import pytest


# ---------------------------------------------------------------------------
# Fake character — mirrors the _FakeChar pattern from test_chassis.py
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
            "bonus_damage": 0,
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

    # --- Real install_profession logic from RobotCharacter ---
    def install_profession(self, profession_id):
        if self.db.profession:
            self.msg("Protocol already installed.")
            return False
        if not self.db.chassis:
            self.msg("Chassis required before protocol installation.")
            return False
        if self.db.level < 3:
            self.msg("Insufficient level. Required: 3.")
            return False
        from world.professions import PROFESSIONS

        prof = PROFESSIONS.get(profession_id)
        if not prof:
            self.msg("Unknown protocol.")
            return False
        self.db.profession = profession_id
        for level, skill_id in prof.get("skills", {}).items():
            if self.db.level >= int(level) and skill_id not in (self.db.skills or []):
                self.db.skills.append(skill_id)
                self.msg(f"Skill unlocked: {skill_id}.")
        self.msg(f"Protocol installed: {prof['name']}. Operational parameters updated.")
        return True

    # --- Real award_xp logic from RobotCharacter ---
    def award_xp(self, amount):
        self.db.experience += amount
        self.msg(f"|yProcessing log: +{amount} XP.|n")
        while self.db.level < 20:
            xp_needed = self.db.level * 100
            if self.db.experience >= xp_needed:
                self.db.level += 1
                if self.db.profession:
                    from world.professions import PROFESSIONS

                    growth = PROFESSIONS[self.db.profession]["growth"]
                    for stat, value in growth.items():
                        current = getattr(self.db, stat, 0)
                        setattr(self.db, stat, current + value)
                else:
                    self.db.max_integrity += 10
                    self.db.processing += 1
                self.db.integrity = min(self.db.integrity + 10, self.db.max_integrity)
                self.msg(f"|gSystem upgrade. Level {self.db.level} reached.|n")
                if self.db.profession:
                    from world.professions import PROFESSIONS

                    skills = PROFESSIONS[self.db.profession].get("skills", {})
                    for level, skill_id in skills.items():
                        if self.db.level >= int(level) and skill_id not in (self.db.skills or []):
                            self.db.skills.append(skill_id)
                            self.msg(f"|gSkill unlocked: {skill_id}.|n")
            else:
                break


# ---------------------------------------------------------------------------
# Helper: create a _FakeChar ready for profession install (chassis + level 3)
# ---------------------------------------------------------------------------


def _ready_char():
    """Return a _FakeChar with chassis set and level 3."""
    char = _FakeChar()
    char._db["chassis"] = "scout"
    char._db["level"] = 3
    char._db["experience"] = 0
    return char


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_install_profession_succeeds():
    """With chassis set and level >= 3, install returns True and sets db.profession."""
    char = _ready_char()

    result = char.install_profession("combat_protocol")

    assert result is True
    assert char.db.profession == "combat_protocol"


def test_install_rejected_without_chassis():
    """Without chassis, install returns False."""
    char = _FakeChar()
    char._db["level"] = 3

    result = char.install_profession("combat_protocol")

    assert result is False
    assert char.db.profession is None


def test_install_rejected_below_level_3():
    """With chassis but level 1, install returns False."""
    char = _FakeChar()
    char._db["chassis"] = "scout"
    # level defaults to 1

    result = char.install_profession("combat_protocol")

    assert result is False
    assert char.db.profession is None


def test_second_install_rejected():
    """Installing a second profession returns False."""
    char = _ready_char()
    char.install_profession("combat_protocol")

    result = char.install_profession("systems_engineer")

    assert result is False
    assert char.db.profession == "combat_protocol"


def test_levelup_uses_profession_growth():
    """After installing combat_protocol, leveling up adds +2 processing (not flat +1)."""
    char = _ready_char()
    char.install_profession("combat_protocol")
    processing_before = char.db.processing

    # Level 3 -> 4 requires 300 XP
    char.award_xp(300)

    assert char.db.level == 4
    assert char.db.processing == processing_before + 2


def test_skills_unlock_at_correct_levels():
    """Installing combat_protocol at level 3 unlocks 'upload_virus'; leveling to 5 unlocks 'overclock'."""
    char = _ready_char()
    char.install_profession("combat_protocol")

    # Level 3 skill should be unlocked on install
    assert "upload_virus" in char.db.skills
    assert "overclock" not in char.db.skills

    # XP threshold check: level N needs N*100 XP (not consumed, just compared).
    # At level 4, needs 400; at level 5, needs 500. Award 499 to reach level 5 but not 6.
    char.award_xp(499)

    assert char.db.level == 5
    assert "overclock" in char.db.skills
