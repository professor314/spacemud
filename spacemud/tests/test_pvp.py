"""
Tests for PVP combat mechanics.

Covers:
- CmdAttack rejects player-vs-player combat outside PVP zones
- CmdAttack allows player-vs-player combat inside PVP zones
- PVP death applies 10% XP penalty to loser and increments winner's pvp_kills
"""

from unittest.mock import PropertyMock, patch

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
class TestPVPCombat(EvenniaTest):
    """Tests for PVP combat mechanics."""

    def _setup_char(self, char, **overrides):
        """Apply standard RobotCharacter attributes to a test character."""
        defaults = {
            "player_state": "active",
            "processing": 10,
            "shielding": 5,
            "integrity": 100,
            "max_integrity": 100,
            "experience": 0,
            "level": 1,
            "credits": 0,
            "chassis": None,
            "bonus_damage": 0,
            "pvp_kills": 0,
        }
        defaults.update(overrides)
        for attr, value in defaults.items():
            setattr(char.db, attr, value)

    def test_attack_player_outside_pvp_zone_rejected(self):
        """Attacking another player in a non-PVP zone sends 'Combat protocol restricted' message."""
        self.room1.db.pvp_zone = False
        self._setup_char(self.char1)
        self._setup_char(self.char2)

        received_messages = []
        original_msg = self.char1.msg

        def capture_msg(text=None, **kwargs):
            if text:
                received_messages.append(str(text))

        self.char1.msg = capture_msg

        from commands.combat import CmdAttack

        cmd = CmdAttack()
        cmd.caller = self.char1
        cmd.args = self.char2.key
        cmd.session = None

        # has_account checks sessions.count(); mock it to True for char2
        # so CmdAttack recognises char2 as a player character.
        char2_class = type(self.char2)
        with patch.object(char2_class, "has_account", new_callable=PropertyMock, return_value=True):
            cmd.func()

        self.char1.msg = original_msg

        self.assertTrue(
            any("Combat protocol restricted" in m for m in received_messages),
            f"Expected 'Combat protocol restricted' message, got: {received_messages}",
        )
        # Player state should remain active (no combat started)
        self.assertEqual(self.char1.db.player_state, "active")

    def test_attack_player_in_pvp_zone_works(self):
        """Attacking another player in a PVP zone starts combat and sets player_state to 'combat'."""
        self.room1.db.pvp_zone = True
        self._setup_char(self.char1)
        self._setup_char(self.char2)

        from commands.combat import CmdAttack

        cmd = CmdAttack()
        cmd.caller = self.char1
        cmd.args = self.char2.key
        cmd.session = None

        char2_class = type(self.char2)
        with patch.object(char2_class, "has_account", new_callable=PropertyMock, return_value=True):
            cmd.func()

        self.assertEqual(self.char1.db.player_state, "combat")

        # A CombatScript should be attached to char1
        scripts = [s for s in self.char1.scripts.all() if s.key == "combat_script"]
        self.assertTrue(len(scripts) >= 1, "No CombatScript found on character")

        # Clean up
        for s in scripts:
            s.stop()
        self.char1.db.player_state = "active"

    def test_pvp_death_applies_xp_penalty(self):
        """PVP death reduces loser's XP by 10% and increments winner's pvp_kills."""
        # Create a Repair Bay so CombatScript can relocate the dead character
        repair_bay = evennia.create_object(
            "typeclasses.rooms.StationRoom",
            key="Repair Bay",
            location=None,
        )

        # char1 is the attacker (will die) — low integrity, some XP
        self._setup_char(self.char1, integrity=1, experience=1000, player_state="combat")
        # char2 is the defender (will kill char1) — massive processing
        self._setup_char(self.char2, processing=999, pvp_kills=0)

        script = evennia.create_script(
            "typeclasses.scripts.CombatScript",
            obj=self.char1,
            persistent=False,
        )
        script.db.attacker = self.char1
        script.db.defender = self.char2

        # has_account must return True for char2 so the PVP death
        # branch in CombatScript.at_repeat fires.
        char2_class = type(self.char2)
        with patch.object(char2_class, "has_account", new_callable=PropertyMock, return_value=True):
            script.at_repeat()

        # XP penalty: 10% of 1000 = 100, so char1 should have 900
        self.assertEqual(
            self.char1.db.experience,
            900,
            f"Expected 900 XP after 10% penalty, got {self.char1.db.experience}",
        )

        # Winner's pvp_kills should be incremented
        self.assertEqual(
            self.char2.db.pvp_kills,
            1,
            f"Expected pvp_kills=1, got {self.char2.db.pvp_kills}",
        )

        # Clean up
        script.stop()
        repair_bay.delete()
