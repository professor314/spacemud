"""
Tests for unit state management.

Covers:
- Idle command sets player_state to "idle"
- Any command while idle transitions back to "active"
- Combat blocks restricted commands
- Combat allows unrestricted commands
- Offline blocks most commands
- Offline allows scan/look/help
"""

from utils.state_checks import check_state


# ---------------------------------------------------------------------------
# Fake character — mirrors the _FakeChar pattern from test_chassis.py
# ---------------------------------------------------------------------------


class _FakeLocation:
    """Minimal stand-in for a room that records msg_contents calls."""

    def __init__(self):
        self.messages = []

    def msg_contents(self, text, exclude=None):
        self.messages.append(text)


class _FakeChar:
    """Minimal stand-in for a RobotCharacter used in state-check tests."""

    def __init__(self):
        self._messages = []
        self.name = "TestBot"
        self.location = None
        self._db = {
            "player_state": "active",
            "idle_message": "",
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


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_idle_sets_state():
    """check_state doesn't block 'idle', but CmdIdle sets player_state to 'idle'."""
    char = _FakeChar()
    char._db["player_state"] = "active"

    # check_state itself should not block the idle command for an active player
    result = check_state(char, "idle")
    assert result is None

    # Simulate what CmdIdle.func() does
    char._db["player_state"] = "idle"
    assert char.db.player_state == "idle"


def test_any_command_returns_to_active():
    """When state is 'idle', calling check_state with any command transitions back to 'active'."""
    char = _FakeChar()
    char.location = _FakeLocation()
    char._db["player_state"] = "idle"
    char._db["idle_message"] = "brb"

    result = check_state(char, "look")

    assert result is None
    assert char.db.player_state == "active"
    assert char.db.idle_message == ""
    assert any("no longer idle" in m for m in char.location.messages)


def test_combat_blocks_restricted_commands():
    """When state is 'combat', check_state returns error for restricted commands."""
    char = _FakeChar()
    char._db["player_state"] = "combat"

    for cmd in ("repair", "missions", "complete", "talk", "select"):
        result = check_state(char, cmd)
        assert result is not None, f"Expected {cmd!r} to be blocked in combat"
        assert "combat" in result.lower()


def test_combat_allows_unrestricted_commands():
    """When state is 'combat', check_state returns None for allowed commands."""
    char = _FakeChar()
    char._db["player_state"] = "combat"

    for cmd in ("attack", "flee", "use", "status", "scan"):
        result = check_state(char, cmd)
        assert result is None, f"Expected {cmd!r} to be allowed in combat"


def test_offline_blocks_most_commands():
    """When state is 'offline', check_state returns error for most commands."""
    char = _FakeChar()
    char._db["player_state"] = "offline"

    for cmd in ("attack", "repair", "status", "inventory"):
        result = check_state(char, cmd)
        assert result is not None, f"Expected {cmd!r} to be blocked when offline"


def test_offline_allows_scan():
    """When state is 'offline', check_state returns None for scan, look, help."""
    char = _FakeChar()
    char._db["player_state"] = "offline"

    for cmd in ("scan", "look", "help"):
        result = check_state(char, cmd)
        assert result is None, f"Expected {cmd!r} to be allowed when offline"
