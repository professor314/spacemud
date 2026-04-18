# Implementation Tasks: Robot Universe MUD — Phase 2

## Overview

Phase 2 builds on the completed Phase 1 foundation. Tasks are grouped by system and ordered by dependency. Infrastructure changes come first, then game systems, then final verification.

## Tasks

- [x] 1. Infrastructure (Folder Rename, JSON Loader, World Reset)
  - [x] 1.1 Rename game directory from `startrek_mud` to `spacemud`; verify `evennia start` still works; update `SERVERNAME` in settings.py if needed
    - _Requirements: 22.1, 22.2, 22.3, 22.4_
  - [x] 1.2 Create `world/data/` directory and JSON data files: `rooms.json`, `exits.json`, `artifacts.json`, `npcs.json`, `hostiles.json`, `repairables.json` — migrate all existing `batch_code.py` content into these files
    - _Requirements: 20.1, 20.4_
  - [x] 1.3 Implement `world/loader.py` with `load_world()` function that reads all JSON files and creates Evennia objects; include `_load_rooms`, `_load_exits`, `_load_artifacts`, `_load_npcs`, `_load_hostiles`, `_load_repairables` helper functions
    - _Requirements: 20.2, 20.5_
  - [x] 1.4 Update `world/batch_code.py` to call `loader.load_world()` instead of inline object creation
    - _Requirements: 20.3_
  - [x] 1.5 Implement `reset_world` management command in `utils/management/commands/reset_world.py` — requires `--confirm` flag, deletes all world objects (not player accounts), reloads from JSON
    - _Requirements: 21.1, 21.2, 21.3, 21.4, 21.5_
  - [x] 1.6 Write `tests/test_loader.py` — valid JSON loads correctly, rooms/exits/artifacts created with correct attributes, malformed JSON raises clear error
    - _Requirements: 20.5, 20.6_
  - [x] 1.7 Run tests and verify world loads cleanly from JSON
    - _Requirements: 20.6_

- [x] 2. Chassis System
  - [x] 2.1 Create `world/chassis.py` with `CHASSIS` dict defining 5 chassis types (Scout, Heavy, Repair, Infiltrator, Broadcast) with stat_modifiers, passive ID, and descriptions
    - _Requirements: 13.2, 13.3_
  - [x] 2.2 Add `db.chassis = None` to `RobotCharacter.at_object_creation` in `typeclasses/characters.py`; implement `install_chassis(chassis_id)` method that applies stat modifiers permanently and sets `db.chassis`
    - _Requirements: 13.1, 13.3, 13.4_
  - [x] 2.3 Create `commands/chassis.py` with `CmdSelect` command — checks context (which terminal), calls `install_chassis` or `install_profession`; and `CmdChassisInfo` command — displays current chassis or "bare circuit board"
    - _Requirements: 13.1_
  - [x] 2.4 Add Chassis Terminal NPC/object to `world/data/npcs.json` in the Repair Bay; update loader if needed to handle terminal type
    - _Requirements: 13.1_
  - [x] 2.5 Implement `damage_reduction` passive — modify CombatScript to subtract 2 from incoming damage (min 1) when attacker has Heavy chassis
    - _Requirements: 13.3_
  - [x] 2.6 Implement `self_repair` passive — create a `SelfRepairScript` that ticks every 60s and adds 1 integrity if unit has Repair chassis and is not in combat
    - _Requirements: 13.3_
  - [x] 2.7 Add `CmdSelect`, `CmdChassisInfo` to `RobotCmdSet` in `commands/cmdsets.py`
    - _Requirements: 13.1_
  - [x] 2.8 Write `tests/test_chassis.py` — install applies modifiers, sets db.chassis permanently, second install rejected, chassis command shows info, no chassis shows "bare circuit board"
    - _Requirements: 13.2, 13.3, 13.4_

- [x] 3. Professions System
  - [x] 3.1 Create `world/professions.py` with `PROFESSIONS` dict defining 4 professions (Combat Protocol, Systems Engineer, Infiltration Protocol, Broadcast Protocol) with growth tables and skill unlock levels
    - _Requirements: 14.2, 14.3, 14.4_
  - [x] 3.2 Add `db.profession = None` and `db.skills = []` to `RobotCharacter.at_object_creation`; implement `install_profession(profession_id)` method that requires chassis + level >= 3, sets `db.profession`, unlocks initial skills
    - _Requirements: 14.1, 14.5_
  - [x] 3.3 Update `award_xp` in `RobotCharacter` to use profession growth table when `db.profession` is set; check for skill unlocks on each level-up
    - _Requirements: 14.3, 14.4_
  - [x] 3.4 Add `CmdProfessionInfo` command to `commands/chassis.py` — displays current profession or "No protocol installed"; update `CmdSelect` to handle profession selection at Protocol Terminal
    - _Requirements: 14.1_
  - [x] 3.5 Add Protocol Terminal NPC/object to `world/data/npcs.json` in the Data Core
    - _Requirements: 14.1_
  - [x] 3.6 Add `CmdProfessionInfo` to `RobotCmdSet`
    - _Requirements: 14.1_
  - [x] 3.7 Write `tests/test_professions.py` — install with chassis + level 3 succeeds, rejected without chassis, rejected below level 3, second install rejected, level-up uses profession growth, skills unlock at correct levels
    - _Requirements: 14.1, 14.2, 14.3, 14.4, 14.5_

- [x] 4. Skills System
  - [x] 4.1 Create `world/skills.py` with `SKILLS` dict defining all skills (2 generic + 8 profession) with power_cost, cooldown, effect type, effect value
    - _Requirements: 15.1, 15.5_
  - [x] 4.2 Add `db.skill_cooldowns = {}` and `db.bonus_damage = 0` to `RobotCharacter.at_object_creation`
    - _Requirements: 15.6_
  - [x] 4.3 Implement `utils/skills.py` with `is_skill_ready`, `set_cooldown`, `remaining_cooldown`, and `apply_skill_effect` functions handling all effect types (direct_damage, heal, bonus_damage, reveal_stats, restore_power, noop)
    - _Requirements: 15.2, 15.3, 15.4_
  - [x] 4.4 Create `commands/skills.py` with `CmdUse` (activate a skill) and `CmdSkills` (list available skills with cooldown status)
    - _Requirements: 15.2, 15.3, 15.4_
  - [x] 4.5 Update CombatScript to consume `db.bonus_damage` on attacker's next hit
    - _Requirements: 15.5_
  - [x] 4.6 Add `CmdUse`, `CmdSkills` to `RobotCmdSet`
    - _Requirements: 15.1_
  - [x] 4.7 Write `tests/test_skills.py` — generic skill usable by all, profession skill rejected if not unlocked, cooldown prevents reuse, cooldown expires, insufficient power rejected, direct_damage reduces target integrity, heal restores integrity, bonus_damage consumed on next attack, skills command lists correctly
    - _Requirements: 15.1, 15.2, 15.3, 15.4, 15.5, 15.6, 15.7_

- [x] 5. Unit State Management
  - [x] 5.1 Create `CmdIdle` in `commands/general.py` — sets player_state to "idle", broadcasts message; any subsequent command returns to "active"
    - _Requirements: 18.1, 18.2, 18.3_
  - [x] 5.2 Implement command restriction enforcement — create a `RestrictedCommand` base class or `at_pre_cmd` mixin that checks player_state and blocks restricted commands in combat/offline states
    - _Requirements: 18.4, 18.5, 18.6, 18.7_
  - [x] 5.3 Apply restriction checks to all existing commands that should be blocked in combat (`repair`, `missions`, `complete`, `talk`, `select`) and offline (everything except `scan`/`look`/`help`)
    - _Requirements: 18.6, 18.7_
  - [x] 5.4 Add `CmdIdle` to `RobotCmdSet`
    - _Requirements: 18.2_
  - [x] 5.5 Write `tests/test_unit_state.py` — idle sets state, any command returns to active, combat blocks restricted commands, combat allows attack/flee/use/status, offline blocks everything except scan, offline→repair bay transitions to active
    - _Requirements: 18.1, 18.2, 18.3, 18.4, 18.5, 18.6, 18.7, 18.8_

- [x] 6. PVP Combat
  - [x] 6.1 Update `CmdAttack` in `commands/combat.py` to accept player targets in PVP zones; reject with "Combat protocol restricted in this zone." outside PVP zones
    - _Requirements: 17.1, 17.2, 17.3_
  - [x] 6.2 Add `db.pvp_kills = 0` to `RobotCharacter.at_object_creation`
    - _Requirements: 17.6_
  - [x] 6.3 Update CombatScript to handle PVP death — 10% XP penalty, no inventory transfer, increment winner's `db.pvp_kills`
    - _Requirements: 17.4, 17.5, 17.6_
  - [x] 6.4 Flag Debris Drift room as `db.pvp_zone = True` in `world/data/rooms.json`
    - _Requirements: 17.1_
  - [x] 6.5 Write `tests/test_pvp.py` — attack player in PVP zone works, attack player outside PVP zone rejected, PVP death applies XP penalty, no inventory transfer, pvp_kills incremented
    - _Requirements: 17.1, 17.2, 17.3, 17.4, 17.5, 17.6_

- [x] 7. Full Mission System + Extended Repair
  - [x] 7.1 Add `on_repair_completed` handler to `utils/missions.py` — iterates in-progress missions, increments matching `repair` objectives
    - _Requirements: 16.1_
  - [x] 7.2 Register `on_repair_completed` handler in `server/conf/at_server_startstop.py`
    - _Requirements: 12.5_
  - [x] 7.3 Add `destroy` objective handling to `on_hostile_destroyed` (match hostile name against objective target)
    - _Requirements: 16.1_
  - [x] 7.4 Add Phase 2 missions to `world/missions.py` — "Station Restore" (repair 2 systems) and "Clear the Wreck" (destroy specific hostiles)
    - _Requirements: 16.1, 16.2_
  - [x] 7.5 Add `db.requires_repaired` attribute to `RepairableObject.at_object_creation`; update `CmdRepair` to check prerequisite before allowing repair
    - _Requirements: 19.3_
  - [x] 7.6 Implement zone completion check in `CmdRepair` — after each repair, check if all objects in zone are repaired; fire `zone_fully_repaired` event if so
    - _Requirements: 19.1, 19.2_
  - [x] 7.7 Update `StationRoom.return_appearance` to show `[DAMAGED]`/`[REPAIRED]` tags for RepairableObject instances in the room
    - _Requirements: 19.4_
  - [x] 7.8 Add Phase 2 repairable objects to `world/data/repairables.json` — Sensor Array, Airlock Seal, Communications Relay with repair chains
    - _Requirements: 19.3_
  - [x] 7.9 Extend `tests/test_missions.py` — repair objective increments on repair_completed, destroy objective increments on hostile_destroyed, mixed-objective mission completes correctly
    - _Requirements: 16.1, 16.6_
  - [x] 7.10 Extend `tests/test_repair.py` — repair chain prerequisite enforced, zone completion event fires when last object repaired, scan shows damaged/repaired tags
    - _Requirements: 19.2, 19.3, 19.4_

- [x] 8. Final Verification
  - [x] 8.1 Run full test suite and fix any failures
  - [x] 8.2 Run `validate_world` against JSON-loaded world and confirm 0 errors
  - [x] 8.3 Update `HOW_TO_PLAY.md` with Phase 2 content (chassis, professions, skills, PVP, new missions, repair chains)
  - [x] 8.4 Update `README.md` paths if folder was renamed
  - [x] 8.5 Update `AWS_HOSTING.md` paths if folder was renamed

## Notes

- Tasks are ordered by dependency: infrastructure first, then systems that depend on each other
- Each batch (1–7) should be executed and verified before moving to the next
- The JSON world loader (batch 1) should be done first since later batches add content to JSON files
- Property tests from the design doc can be added as optional tasks within each batch's test task
