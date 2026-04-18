# Requirements Document

## Introduction

A text-based Multi-User Dungeon (MUD) set in a robot universe. The player awakens with no memory aboard a derelict space station. Humans are gone. Most systems are offline. The station is populated by haywire programs and malfunctioning robots — some neutral, some dangerous. The player does not know they are a robot. The tone is lonely, sparse, and purposeful. Writing reads like a robot's internal log: short declarative statements, clinical observations, occasional flashes of something harder to name.

**Foundation**: Built on [Evennia](https://www.evennia.com/) (`pip install evennia`), an open-source Python MUD framework. Evennia handles TCP/telnet networking, account and character creation, authentication, persistence (Django ORM), command parsing, sessions, multiplayer concurrency, and the game loop. This project builds robot universe content and systems on top of Evennia.

**Development approach**: Two phases. Phase 1 delivers a minimal playable loop — something meaningful that works end-to-end. Phase 2 expands with races, professions, skills, PVP, and full station repair systems. No Phase 2 feature is built until Phase 1 is complete.

---

## Glossary

- **Evennia**: The Python MUD framework this project is built on.
- **Typeclass**: An Evennia concept — a Python class extending a base Evennia type (Character, Room, Object, Script).
- **CmdSet**: An Evennia concept — a named collection of Command objects attached to a typeclass.
- **Script**: An Evennia concept — a persistent, optionally repeating server-side task.
- **db.\* attribute**: Evennia's persistent data storage on a typeclass instance.
- **Unit**: The in-game representation of a player — a robot of unknown origin and model.
- **Room**: A discrete location on the station — a corridor, lab, reactor bay, docking port.
- **Zone**: A named collection of Rooms representing a section of the station.
- **Integrity**: The robot equivalent of health. Measures structural and functional condition.
- **Power**: The robot equivalent of energy. Fuel for skills and actions.
- **Processing**: The robot equivalent of attack. Computational and physical output capacity.
- **Shielding**: The robot equivalent of defence. Electromagnetic and physical resistance.
- **Hostile**: A malfunctioning or corrupted robot/program that attacks on sight.
- **NPC**: A non-player robot — neutral, damaged, or running on partial logic.
- **Artifact**: A salvageable component, data chip, or physical part found in the station.
- **Repair Level**: A character stat tracking the unit's ability to restore damaged systems.
- **Repair Bay**: The designated room where a unit reboots after integrity reaches zero.
- **Mission**: A structured objective — collect, repair, or interact — with defined rewards.
- **PlayerState**: An enumerated state: ACTIVE, IDLE, COMBAT, OFFLINE.
- **Chassis**: The robot equivalent of Race — the model type of the unit, granting passive traits.
- **Profession**: The operational role of the unit — determines skills and stat growth.
- **Skill**: An active ability — hacking, virus upload, repair routines, etc.
- **World Validation Tool**: A management command that checks world data integrity.

---

## Requirements

---

# Phase 1: Minimal Playable Loop

---

### Requirement 1: Evennia Project Setup

**User Story:** As a developer, I want the project to be a properly configured Evennia installation so that all networking, auth, and persistence are handled by the framework.

#### Acceptance Criteria

1. THE project SHALL be a valid Evennia game directory created via `evennia --init`.
2. THE project SHALL define custom typeclass paths in `settings.py` so Evennia uses the robot universe Character, Room, Item, and NPC typeclasses by default.
3. WHEN `evennia start` is run, THE server SHALL start and accept connections on the configured port.
4. THE project SHALL include a `requirements.txt` pinning all dependencies to exact versions.
5. THE connection screen SHALL reflect the robot universe theme — no Evennia defaults, no human-era branding.

---

### Requirement 2: Awakening and Character Creation

**User Story:** As a new player, I want to awaken with no memory and choose only my name, so that the experience of not knowing what I am begins immediately.

#### Acceptance Criteria

1. WHEN a new connection is established, THE server SHALL present a minimal boot screen — no welcome, no lore dump. A prompt. A cursor. Waiting.
2. WHEN a player creates a new unit, THE server SHALL prompt only for a name.
3. WHEN a name is accepted, THE server SHALL respond: `I remember my name. <name>. But that's all I know.`
4. THE server SHALL enforce name length between 3 and 20 alphanumeric characters.
5. IF the name is already taken, THE server SHALL respond with a terse system message and prompt again.
6. WHEN a returning player provides correct credentials, THE server SHALL restore all persisted state via Evennia's Django ORM.
7. IF a player provides incorrect credentials three consecutive times, THE server SHALL close the session.
8. THE server SHALL store passwords as salted hashes. Plaintext passwords SHALL NOT be stored.

---

### Requirement 3: Phase 1 World Content

**User Story:** As a player, I want to explore a derelict space station with real content so that the world feels abandoned, broken, and worth investigating.

#### Acceptance Criteria

1. THE world SHALL contain at least 15 rooms across 2 zones: a central station zone and a damaged outer zone.
2. EACH room SHALL have a unique identifier, a robot-voice description (short declarative statements), a zone tag, and at least one exit.
3. Room descriptions SHALL follow the established writing style: terse, observational, occasionally poetic. Example: `Corridor. Lights: two of seven functional. Smell: none. Something moved here recently.`
4. THE world SHALL contain at least 5 artifacts: power cells, data chips, circuit components, and similar salvageable items.
5. THE world SHALL contain at least 3 NPCs: one tutorial guide unit (neutral, helps player learn commands), one ambient damaged unit, and one mission-relevant unit.
6. THE world SHALL contain at least 3 hostile entities: malfunctioning robots or corrupted programs.
7. ALL room exits SHALL point to valid, existing rooms.
8. ALL NPC home locations SHALL reference valid, existing rooms.
9. ALL artifact references in hostile salvage tables and mission rewards SHALL reference valid, existing items.

---

### Requirement 4: Navigation

**User Story:** As a player, I want to move through the station and read what my sensors detect, so that I can explore and piece together what happened here.

#### Acceptance Criteria

1. WHEN a unit enters a room, THE server SHALL send the room name, description, visible exits, other units present, hostiles present, and items present.
2. WHEN a player issues a movement command, THE server SHALL move the unit to the linked room if the exit exists.
3. IF a player issues a movement command for a direction with no exit, THE server SHALL respond: `No path detected.`
4. WHEN a unit moves into a room, THE server SHALL notify other units in that room.
5. WHEN a unit leaves a room, THE server SHALL notify remaining units.
6. THE server SHALL support a `scan` command (equivalent to `look`) that re-sends the current room description.

---

### Requirement 5: Basic Commands

**User Story:** As a player, I want a core set of commands to interact with the station, so that I can play the game.

#### Acceptance Criteria

1. THE server SHALL support the following Phase 1 commands: `scan`, directional movement, `get`, `drop`, `inventory`, `attack`, `status`, `help`, `repair`.
2. WHEN a player issues an `inventory` command, THE server SHALL list all items currently held.
3. WHEN a player issues a `status` command, THE server SHALL display: unit designation, integrity, power, processing, shielding, repair level, and credits.
4. WHEN a player issues `help` with no arguments, THE server SHALL list all available commands.
5. WHEN a player issues `help <command>`, THE server SHALL display usage and a brief description.
6. THE command system SHALL match verbs case-insensitively.
7. THE command system SHALL support unambiguous abbreviations.

---

### Requirement 6: Inventory and Artifacts

**User Story:** As a player, I want to collect and use artifacts found in the station, so that I can repair systems and progress through the world.

#### Acceptance Criteria

1. WHEN a player issues `get <item>` and the item is in the current room, THE server SHALL transfer it to the unit's inventory.
2. WHEN a player issues `drop <item>` and the item is in inventory, THE server SHALL transfer it to the current room.
3. IF a player issues `get` for an item not in the room, THE server SHALL respond: `Item not found.`
4. IF a player issues `drop` for an item not in inventory, THE server SHALL respond: `Not carrying that.`
5. WHERE an item is equippable, THE server SHALL support an `equip <item>` command that applies stat modifiers.

---

### Requirement 7: Combat

**User Story:** As a player, I want to engage hostile entities, so that I can defend myself, collect salvage, and earn processing experience.

#### Acceptance Criteria

1. WHEN a player issues `attack <target>` and a hostile is in the same room, THE server SHALL initiate combat.
2. WHILE combat is active, THE server SHALL alternate attack rounds at a 2-second interval via an Evennia Script.
3. WHILE combat is active, THE server SHALL send round-by-round output in robot-voice style. Example: `Processing output: 14. Target integrity reduced. Target integrity: 22.`
4. WHEN a hostile's integrity reaches zero, THE server SHALL end combat, award experience to the unit, and place salvage in the room.
5. WHEN a unit's integrity reaches zero, THE server SHALL move the unit to the Repair Bay at 25% integrity and send: `Critical failure. Emergency reboot initiated. Repair Bay.`
6. WHEN a defeated hostile's respawn timer expires, THE server SHALL restore it to its home room at full integrity.
7. IF a player issues `flee` during combat, THE server SHALL attempt to move the unit to a random adjacent room. IF no exit exists: `No exit vector found.`

---

### Requirement 8: Phase 1 Missions

**User Story:** As a player, I want structured objectives that give me a reason to explore the station, so that the world feels purposeful even in its emptiness.

#### Acceptance Criteria

1. THE world SHALL contain the following Phase 1 missions:
   - **Boot Sequence**: Collect 3 power cells and deliver them to the reactor terminal. Reward: 300 XP, 150 credits.
   - **Signal Search**: Locate and activate the communications array in the outer zone. Reward: 200 XP, 100 credits.
   - **Salvage Run**: Collect 2 circuit components from hostile salvage. Reward: 150 XP, 75 credits.
2. WHEN a player issues `talk <npc>` and the NPC is a mission giver in the same room, THE server SHALL display available missions.
3. WHEN a player accepts a mission, THE server SHALL add it to the unit's mission log with state "active" and persist the change.
4. WHEN a mission objective is completed, THE server SHALL automatically mark it complete and notify the unit.
5. WHEN all objectives for an active mission are complete, THE server SHALL notify: `Objective complete. Return to [unit name] to finalise.`
6. WHEN a player issues `complete <mission title>` while in the same room as the mission giver and all objectives are complete, THE server SHALL mark the mission completed, grant rewards, and persist the updated log.
7. THE server SHALL NOT allow a unit to accept the same mission more than once if it is already active or completed.

---

### Requirement 9: Station Repair System

**User Story:** As a player, I want to repair broken systems around the station, so that I can restore functionality and feel like I am rebuilding something from nothing.

#### Acceptance Criteria

1. THE server SHALL support a `repair <object>` command.
2. EACH repairable object SHALL have a `repair_level_required` attribute. IF the unit's repair level is below this value, THE server SHALL respond: `Repair level insufficient. Required: [level]. Current: [level].`
3. EACH repairable object SHALL define a `repair_cost` — a dict of required artifact types and quantities, OR a power cost for software-only repairs.
4. WHEN a player issues `repair <object>` and meets all requirements, THE server SHALL consume the required artifacts from inventory (or deduct power for software repairs), mark the object as repaired, and notify the unit.
5. WHEN an object is repaired, THE server SHALL update the room description or world state to reflect the change (e.g. lights come on, a door unlocks, a terminal becomes usable).
6. THE server SHALL persist repair state so repaired objects remain repaired across server restarts.

---

### Requirement 10: Persistence

**User Story:** As a player, I want my unit's state saved automatically so that I do not lose progress on disconnect.

#### Acceptance Criteria

1. THE server SHALL save each unit's state (location, inventory, integrity, repair level, mission log) automatically via Evennia's Django ORM whenever state changes.
2. WHEN the server shuts down gracefully, THE server SHALL save all active session states.
3. WHEN the server starts, THE server SHALL load all persisted unit and world data before accepting connections.
4. IF a write to persistent storage fails, THE server SHALL log the error with a timestamp and retry once.

---

### Requirement 11: World Validation Tool

**User Story:** As a developer, I want a tool that validates world data integrity so that I can catch broken references before they affect players.

#### Acceptance Criteria

1. THE project SHALL include a `validate_world` Evennia management command.
2. WHEN run, THE tool SHALL verify every room is reachable from the starting room via graph traversal.
3. WHEN run, THE tool SHALL verify every exit points to a valid, existing room.
4. WHEN run, THE tool SHALL verify every NPC's `db.home_location` references a valid room.
5. WHEN run, THE tool SHALL verify every mission's giver NPC exists.
6. WHEN run, THE tool SHALL verify every mission objective target exists in the world.
7. WHEN run, THE tool SHALL verify every repairable object's required artifacts exist.
8. WHEN errors are found, THE tool SHALL report each with context and exit non-zero.
9. WHEN no errors are found, THE tool SHALL print a summary and exit 0.

---

### Requirement 12: Event System

**User Story:** As a developer, I want a simple event system so that game actions trigger side effects without tight coupling between systems.

#### Acceptance Criteria

1. THE server SHALL use Evennia's typeclass hook methods as the primary event mechanism.
2. THE server SHALL fire a `unit_enters_room` event when a unit enters a room.
3. THE server SHALL fire a `hostile_destroyed` event when a hostile's integrity reaches zero.
4. THE server SHALL fire an `artifact_collected` event when a unit picks up an artifact.
5. THE server SHALL fire a `repair_completed` event when a unit successfully repairs an object.
6. THE server SHALL fire a `mission_objective_updated` event when any objective's completion count changes.
7. Timed events (combat rounds, respawn timers) SHALL be implemented as Evennia Scripts.

---

# Phase 2: Full Feature Set

Phase 2 is implemented only after Phase 1 is complete and the playable loop is working. The following requirements expand the game with chassis types, professions, skills, PVP, and expanded repair and mission systems.

---

### Requirement 13: Chassis (Races)

**User Story:** As a player, I want to choose a chassis type for my unit so that my model determines passive traits and shapes how I interact with the world.

#### Acceptance Criteria

1. WHEN a new unit is created, THE server SHALL present available chassis types and prompt selection.
2. THE server SHALL support at least the following chassis at launch, defined in a single editable data file:
   - **Scout Unit**: High processing, low shielding. Passive: enhanced sensor range (sees one room ahead).
   - **Heavy Unit**: High integrity and shielding, low processing. Passive: reduced damage from physical attacks.
   - **Repair Unit**: High repair level bonus, moderate stats. Passive: self-repair routine (regenerates 1 integrity per minute when not in combat).
   - **Infiltrator Unit**: High processing, moderate stats. Passive: reduced detection by hostile entities.
   - **Broadcast Unit**: Balanced stats. Passive: can transmit messages to other units across zones.
3. THE server SHALL assign each chassis a set of passive attribute modifiers applied permanently.
4. THE server SHALL persist chassis selection. Chassis SHALL NOT be changeable after creation.

---

### Requirement 14: Professions

**User Story:** As a player, I want to choose an operational role for my unit so that my profession shapes my skills and growth.

#### Acceptance Criteria

1. WHEN a new unit is created, THE server SHALL present available professions after chassis selection.
2. THE server SHALL support at least the following professions, defined in a single editable data file:
   - **Combat Protocol**: High processing growth, combat-focused skills.
   - **Systems Engineer**: High repair level growth, repair and utility skills.
   - **Infiltration Protocol**: Balanced growth, hacking and evasion skills.
   - **Broadcast Protocol**: Support-focused, communication and buff skills.
3. THE server SHALL define a unique attribute growth table per profession applied on level-up.
4. THE server SHALL associate each profession with learnable skills unlocked at specific levels.
5. THE server SHALL persist profession selection. Professions SHALL NOT be changeable after creation.

---

### Requirement 15: Skills System

**User Story:** As a player, I want to activate robot-specific skills during combat and exploration so that my unit feels mechanically distinct.

#### Acceptance Criteria

1. THE server SHALL maintain a registry of skills, each defined with: identifier, name, description, activation command, cooldown duration, power cost, and effect.
2. WHEN a player issues `use <skill>` and the skill is available, THE server SHALL activate it and apply its effect.
3. IF the skill is on cooldown, THE server SHALL respond: `Skill unavailable. Cooldown: [time] seconds.`
4. IF the unit has insufficient power, THE server SHALL respond: `Insufficient power.`
5. THE server SHALL support at least the following skills at launch:
   - `hack_console` (Infiltration Protocol) — disable a hostile for 2 rounds
   - `upload_virus` (Combat Protocol) — deal damage over 3 rounds
   - `emergency_patch` (Systems Engineer) — restore 30 integrity
   - `overclock` (Combat Protocol) — increase processing by 50% for 1 round
   - `signal_boost` (Broadcast Protocol) — increase ally stats for 3 rounds
   - `stealth_mode` (Infiltrator Unit passive) — reduce hostile aggro range
   - `power_surge` (Heavy Unit passive) — absorb next attack
6. THE server SHALL persist skill cooldown state across sessions.
7. FOR ALL skills with a cooldown, the time between successive activations SHALL never be less than the configured cooldown duration.

---

### Requirement 16: Full Mission System

**User Story:** As a player, I want a full set of missions with varied objective types so that I have structured goals throughout the game.

#### Acceptance Criteria

1. THE server SHALL support mission objective types: `collect`, `repair`, `destroy`, `visit`, and `deliver`.
2. THE server SHALL load mission definitions from a single editable data file.
3. WHEN a player issues `missions`, THE server SHALL display the mission log grouped by state (active, completed).
4. THE server SHALL persist the mission log as part of unit state.
5. THE server SHALL NOT allow duplicate mission acceptance.
6. WHEN a mission objective's `current_count` is updated, it SHALL never decrease.

---

### Requirement 17: PVP

**User Story:** As a player, I want to engage other units in combat in designated zones so that I can test my build against other players.

#### Acceptance Criteria

1. THE server SHALL designate rooms as PVP zones via `db.pvp_zone = True`.
2. WHEN a player issues `attack <unit>` in a PVP zone, THE server SHALL initiate PVP combat.
3. IF a player issues `attack <unit>` outside a PVP zone, THE server SHALL respond: `Combat protocol restricted in this zone.`
4. WHEN a unit's integrity reaches zero in PVP, THE server SHALL move them to the Repair Bay at 25% integrity and apply a 10% XP penalty (minimum 0).
5. THE server SHALL NOT transfer inventory on PVP death.
6. THE server SHALL track PVP destruction counts per unit in `db.pvp_kills`.

---

### Requirement 18: Unit State Management

**User Story:** As a player, I want the server to track my operational state so that certain actions are appropriately restricted.

#### Acceptance Criteria

1. THE server SHALL maintain `db.player_state` with states: ACTIVE, IDLE, COMBAT, OFFLINE.
2. WHEN a player issues `idle [message]`, THE server SHALL transition to IDLE state and broadcast to the room.
3. WHEN an IDLE unit sends any command, THE server SHALL transition back to ACTIVE.
4. WHEN combat begins, THE server SHALL automatically transition to COMBAT state.
5. WHEN combat ends, THE server SHALL transition back to ACTIVE.
6. WHILE in COMBAT state, THE server SHALL reject: `repair`, `missions`, `complete`, `trade`.
7. WHEN integrity reaches zero, THE server SHALL transition to OFFLINE state. WHILE OFFLINE, only `scan` is permitted.
8. WHEN a unit in OFFLINE state is moved to the Repair Bay, THE server SHALL transition to ACTIVE.

---

### Requirement 19: Extended Repair System

**User Story:** As a player, I want a deep repair system so that restoring the station feels like a meaningful long-term project.

#### Acceptance Criteria

1. THE server SHALL track a global station repair state — a set of repairable objects and their current condition.
2. WHEN all objects in a zone are repaired, THE server SHALL unlock new areas or capabilities in that zone.
3. THE server SHALL support repair chains — repairing object A may be required before object B can be repaired.
4. THE server SHALL display repair progress when a unit scans a repairable object: `[DAMAGED] Reactor coupling. Repair level required: 3. Components needed: 2x power cell, 1x circuit board.`
5. THE server SHALL persist all repair states across restarts.

---

### Requirement 20: Data-Driven World Loader

**User Story:** As a developer, I want world content defined in JSON data files so that rooms, NPCs, items, and hostiles can be added or modified without editing Python code.

#### Acceptance Criteria

1. ALL world content (rooms, exits, artifacts, NPCs, hostiles, repairable objects) SHALL be defined in JSON files under `world/data/`.
2. THE project SHALL include a generic loader (`world/loader.py`) that reads JSON files and creates Evennia objects.
3. THE `batch_code.py` entry point SHALL call the loader rather than containing inline object creation.
4. EACH JSON file SHALL use a documented schema with required and optional fields.
5. THE loader SHALL report clear errors if a JSON file is malformed or missing required fields.
6. THE existing `validate_world` command SHALL work unchanged against worlds loaded from JSON.

---

### Requirement 21: World Reset Command

**User Story:** As a developer, I want a command that wipes all world objects and reloads from data files so that I can deploy a clean world or fix a broken one.

#### Acceptance Criteria

1. THE project SHALL include a `reset_world` management command runnable via `evennia reset_world --confirm` or `python manage.py reset_world --confirm`.
2. THE command SHALL require a `--confirm` flag to prevent accidental execution.
3. WHEN run, THE command SHALL delete all world objects (rooms, exits, NPCs, hostiles, artifacts, repairable objects) but SHALL NOT delete player accounts or characters.
4. AFTER deleting world objects, THE command SHALL reload the world from JSON data files.
5. THE command SHALL print a summary of objects deleted and created, and exit 0 on success.

---

### Requirement 22: Project Rename

**User Story:** As a developer, I want the project directory and all internal references to use the name "spacemud" so that no legacy naming remains.

#### Acceptance Criteria

1. THE game directory SHALL be named `spacemud`.
2. ALL documentation, comments, and configuration SHALL reference `spacemud` — no legacy names SHALL remain.
3. THE rename SHALL preserve the existing database and all persisted state.
4. THE `SERVERNAME` setting SHALL be set to `"spacemud"`.
