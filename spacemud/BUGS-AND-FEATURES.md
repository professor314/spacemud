# Space MUD — Bugs & Feature Requests

## Bugs (Broken)

### 1. Combat doesn't tick
- **Severity:** Critical — core gameplay is non-functional
- **Symptom:** `attack <hostile>` prints "Engaging [target]." but no damage rounds ever fire. No damage is dealt to either side. Character stays at full health indefinitely.
- **Likely cause:** The combat system uses an Evennia Script that ticks every 2 seconds to process combat rounds. After the database reset, this script was never recreated. The `attack` command probably starts a Script object that didn't survive the world reload.
- **Where to look:** `commands/combat.py` — find where combat rounds are scheduled. Check if it creates a Script or uses `utils.delay()`. Verify the script is being started on `attack` and that it references valid objects.
- **Reproduction:** Connect, go to Breached Lab (east from Collapsed Corridor), type `attack drone`. Nothing happens after "Engaging."

### 2. No quit confirmation message
- **Severity:** Low — UX polish
- **Symptom:** When a player types `quit`, they are disconnected but receive no confirmation message before disconnection (e.g. "Unit shutting down. Session terminated."). The web client just shows the reconnect dialog.
- **Desired behavior:** Print a short farewell message in robot-voice before disconnecting, e.g. "Systems powering down. Unit state preserved. Reconnect at any time."

## Feature Requests

### 3. Hostile respawning
- **Priority:** High — without this, the world becomes empty permanently
- **Problem:** Once a hostile is killed, it's gone forever. If one player clears all hostiles, there's nothing left for anyone else to fight. The world becomes a dead, safe hallway.
- **Desired behavior:** Hostiles respawn after a set time (e.g. 2–5 minutes) in their original room. A simple timer-based respawn is fine. This could be an Evennia Script that periodically checks if a hostile's room is empty and recreates it from the JSON data.
- **Design note:** Respawned hostiles should be identical to the originals (same stats, same drops). Don't scale them. The world is small enough that a fixed population is fine.

### 4. Repairable systems need to be per-character or repeatable
- **Priority:** High — progression blocker for multiplayer
- **Problem:** Repairable objects (Reactor Coupling, Sensor Array, etc.) are world-shared. Once one player repairs them, they're fixed for everyone. A second player can never repair them, which means they can't earn XP from repair actions and can't progress their repair level.
- **Options:**
  - A) Make repairs per-character (each player sees their own repair state) — more complex
  - B) Make repaired systems degrade over time and need re-repair — simpler, fits the "station is failing" theme
  - C) Add repeatable repair tasks that don't affect the world state (e.g. "diagnostic runs" that give XP but don't change the system's visible state)
- **Recommendation:** Option B — systems degrade back to "damaged" after X minutes (maybe 10–15). This gives every player something to do and reinforces the theme that the station is always breaking down.

### 5. XP sources need to be renewable
- **Priority:** High — related to #3 and #4
- **Problem:** If hostiles don't respawn and repairs are one-time, a player can exhaust all XP sources in the game. They hit a wall where they can't level up, can't unlock professions (requires level 3), and have nothing to do.
- **Desired behavior:** Between hostile respawns (#3) and repeatable repairs (#4), there should always be a way to earn XP. Missions should also be repeatable or have daily resets.

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
