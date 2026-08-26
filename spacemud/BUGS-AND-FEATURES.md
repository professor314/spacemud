# Space MUD — Bugs & Feature Requests

## Bugs (Broken)

### 1. ~~Combat doesn't tick~~ ✅ FIXED
- **Fix:** `_start_combat()` now uses `autostart=False` when creating the CombatScript, sets `db.attacker`/`db.defender`, then calls `script.start()`. This prevents the race condition where `at_repeat()` fires before combatants are set.
- **Deployed:** 2026-08-25

### 2. ~~No quit confirmation message~~ ✅ FIXED
- **Fix:** Custom `CmdQuit` command added with farewell message: "Systems powering down. Unit state preserved. Reconnect at any time."
- **Deployed:** 2026-08-25

## Feature Requests

### 3. ~~Hostile respawning~~ ✅ IMPLEMENTED (was already in code)
- **Status:** Already working. `RespawnScript` fires after `respawn_delay` seconds (90-150s per hostile). Hostiles are removed from world on death and reappear at home location when timer fires.
- **Verified:** Code in `typeclasses/scripts.py` (RespawnScript) + `typeclasses/objects.py` (Hostile.at_death triggers it)

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

### 7. Idle/AFK behavior improvements
- **Priority:** Low
- **Current state:** 30-minute idle timeout kicks players. The `idle` command sets status manually.
- **Possible additions:**
  - Auto-idle after 5 minutes of no input (shows idle status to other players)
  - Warning message at 25 minutes ("Session timeout in 5 minutes. Type any command to stay connected.")
  - The timeout warning IS configured (IDLE_TIMEOUT_WARNING = 60), but verify it actually displays

### 8. Web client landing page
- **Priority:** Low — cosmetic
- **Problem:** The default Evennia homepage shows at `play.imadestuff.com:4001` with "Welcome to Evennia!" text and links to Evennia docs. Players have to click "Play Online" to get to the actual game client.
- **Desired behavior:** Either redirect `/` straight to `/webclient/`, or customize the homepage to be a Space MUD landing page (game description, "Play Now" button, maybe the HOW_TO_PLAY content).

### 9. Connection screen improvements
- **Priority:** Low — polish
- **Ideas:**
  - After `create`, auto-connect the player instead of making them type `connect` again
  - Show a brief "what to do first" hint after connecting (or rely on the Main Corridor tutorial hint)
  - Add `help commands` that lists all available commands in a categorized format

## Notes

- Bugs #1 is the top priority — without combat, most of the game is inert.
- Features #3, #4, #5 are all related to "the world needs to be renewable, not exhaustible." Solve them together.
- Feature #6 is a test plan, not a code change — run it after the bugs are fixed.
