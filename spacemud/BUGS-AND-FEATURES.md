# Space MUD — Bugs & Feature Requests

## Bugs (Broken)

### 1. ~~Combat doesn't tick~~ ✅ FIXED
- **Fix (2026-08-25):** `_start_combat()` uses `autostart=False`, sets
  `db.attacker`/`db.defender`, then calls `script.start()`.
- **Additional fix (2026-09-29):** hardened `_start_combat()` ordering — set the
  combatants AND `player_state="combat"` *before* `script.start()`, and start the
  timer with explicit `interval=2, start_delay=False`. The CombatScript's first
  round fires immediately (Evennia `start_delay` defaults False), so state must be
  set beforehand. Added regression tests (`TestCombatTickRegression`).
- **Verified:** 78/78 tests pass under Python 3.12 + Evennia 6.0.0.

### 2. ~~No quit confirmation message~~ ✅ FIXED
- **Fix:** Custom `CmdQuit` command added with farewell message: "Systems powering down. Unit state preserved. Reconnect at any time."
- **Deployed:** 2026-08-25

## Feature Requests

### 3. ~~Hostile respawning~~ ✅ FIXED (was respawning instantly)
- **Bug (found 2026-09-29):** `RespawnScript` set `interval=respawn_delay`,
  `repeats=1`, `persistent=True` but NOT `start_delay=True`. Evennia's `start_delay`
  defaults to `False`, so the single `at_repeat` fired *immediately* when the script
  was attached on death — hostiles respawned instantly instead of after 90–150 s.
- **Fix:** set `self.start_delay = True` in `RespawnScript.at_script_creation`.
  `RepairDegradeScript` had the identical bug (repaired systems degraded instantly)
  and was fixed the same way.
- **Verified:** `TestRespawnTiming` + `TestRepairDegradeTiming` pass (78/78 suite).

### 4. ~~Repairable systems need to be per-character or repeatable~~ ✅ FIXED
- **Fix:** Option B implemented — `RepairDegradeScript` makes repaired systems degrade back to damaged after 10 minutes (configurable via `db.degrade_delay`). Triggered automatically when any system is repaired.
- **Result:** Every player always has something to repair. XP from repairs is now renewable.
- **Deployed:** 2026-08-25

### 5. ~~XP sources need to be renewable~~ ✅ RESOLVED
- **Status:** Resolved by fixes #3 (hostile respawning was already working) and #4 (repairs now repeatable). Between respawning hostiles and degrading repairs, XP is always available.

### 6. Full playthrough verification
- **Priority:** Medium — QA task
- **Task:** A single player should be able to accomplish the complete game loop:
  1. Create character → spawn in Main Corridor
  2. Explore all rooms, learn all commands via tutorial hints
  3. Pick up items (get)
  4. Select a chassis (Repair Bay)
  5. Fight hostiles and gain XP (outer zone)
  6. Repair systems and gain XP
  7. Complete at least one mission
  8. Reach level 3 and select a profession (Data Core)
  9. Use profession skills
  10. Reach the PVP zone
- **Currently broken at step 5** (combat doesn't tick). Once combat is fixed, run through the full loop and verify each step works.

### 6. Full playthrough verification
- **Priority:** Medium — QA task
- **Status:** ✅ Can now be performed. Combat is fixed, respawning works, repairs are repeatable.
- **Task:** Connect and run through the full game loop (see steps below). Report any issues found.

### 7. ~~Idle/AFK behavior improvements~~ ✅ RESOLVED
- **Status:** Evennia's built-in idle handling covers this:
  - 30-minute timeout (`IDLE_TIMEOUT = 1800`)
  - 60-second warning before kick (`IDLE_TIMEOUT_WARNING = 60`)
  - Custom disconnect message configured
  - Manual `idle` command available for status setting
- **Deployed:** Already in settings.py

### 8. ~~Web client landing page~~ ✅ FIXED
- **Fix:** Custom `index.html` template with game description, command reference, and "Play Now" button linking to `/webclient/`. Styled in terminal green-on-black aesthetic.
- **Deployed:** 2026-08-25

### 9. ~~Connection screen improvements~~ ✅ FIXED
- **Fix:** Added `at_post_puppet` hook that shows unit status and orientation message on connect. `help` command already lists all commands by category.
- **Deployed:** 2026-08-25

## Notes

- All critical bugs and high-priority features are resolved.
- Feature #6 (full playthrough) is a test plan — run it manually to verify the complete game loop works end-to-end.
