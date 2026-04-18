# Space MUD — Setup Guide

A text-based multiplayer game set on a derelict space station. You are a robot. You don't know that yet. Built on [Evennia](https://www.evennia.com/).

---

## Requirements

- Python 3.10+
- Evennia 6.0.0

---

## Quick Start (Scripts)

All scripts are in `scripts/`. Run them from inside the `spacemud/` directory.

```powershell
cd "path/to/Space MUD/spacemud"
```

| Script | What it does |
|---|---|
| `.\scripts\setup.ps1` | First-time: install deps, migrate DB, start server |
| `.\scripts\load-world.ps1` | Load world content from JSON (run once after setup) |
| `.\scripts\start.ps1` | Start the server |
| `.\scripts\stop.ps1` | Stop the server |
| `.\scripts\reload.ps1` | Reload after code changes (no disconnect) |
| `.\scripts\reset-world.ps1` | Wipe and reload world (with confirmation) |
| `.\scripts\test.ps1` | Run the test suite |

### First-Time Setup

```powershell
.\scripts\setup.ps1
```

This installs dependencies, runs the database migration, and starts the server. You'll be prompted to create a superuser account (name + password, at least 8 characters).

Then in a **second** terminal:

```powershell
.\scripts\load-world.ps1
```

This loads all rooms, NPCs, artifacts, hostiles, and repairable objects from JSON data files, then reloads the server so the changes take effect.

After the script finishes, go to the browser. If you're still in Limbo, disconnect (`quit`) and reconnect (`connect <name> <password>`), then type `look`.

### After Setup

```powershell
.\scripts\start.ps1
```

Open your browser to **http://localhost:4001** — that's the web client.

---

## Manual Setup (Without Scripts)

If you prefer running commands manually:

```powershell
cd "path/to/Space MUD/spacemud"
pip install -r requirements.txt
evennia migrate
evennia start
```

Then in a second terminal:

```powershell
python -c "import evennia; evennia._init(); from world.batch_code import main; main(type('C',(),{'msg':staticmethod(print)})())"
```

---

## Connecting

Open your browser to:

```
http://localhost:4001
```

That's the built-in web client. No telnet needed.

---

## World Data

All world content is defined in JSON files under `world/data/`:

| File | Contents |
|---|---|
| `rooms.json` | 15 rooms across 2 zones |
| `exits.json` | 28 bidirectional exits |
| `artifacts.json` | 5 artifacts (components, equipment, quest items) |
| `npcs.json` | 5 NPCs (mission givers, terminals, ambient) |
| `hostiles.json` | 3 hostile entities |
| `repairables.json` | 5 repairable station systems |

Game data files (not JSON):

| File | Contents |
|---|---|
| `world/missions.py` | 5 missions with varied objective types |
| `world/chassis.py` | 5 chassis types with stat modifiers and passives |
| `world/professions.py` | 4 professions with growth tables and skill unlocks |
| `world/skills.py` | 10 skills (2 generic + 8 profession-locked) |

To expand the world, edit the JSON files and run `.\scripts\reset-world.ps1`.

---

## Resetting the World

If you need a clean slate (e.g., after editing JSON data files):

```powershell
.\scripts\reset-world.ps1
```

This deletes all world objects, reloads from JSON, and reloads the server. Player accounts and characters are preserved. After it finishes, disconnect and reconnect in the browser.

---

## Reloading After Code Changes

If you change Python files (not JSON), reload without disconnecting players:

```powershell
.\scripts\reload.ps1
```

**Important:** You must be inside the `spacemud` directory when running any script or `evennia` command.

**Note:** After a reload, connected players may need to disconnect and reconnect to see changes to typeclasses or commands. World data changes (JSON edits) require `.\scripts\reset-world.ps1` instead.

---

## Running the Tests

```powershell
.\scripts\test.ps1
```

73 tests covering combat, items, missions, repair, chassis, professions, skills, PVP, unit state, validation, and the JSON loader.

---

## Other Docs

- **[HOW_TO_PLAY.md](HOW_TO_PLAY.md)** — Player guide with commands, map, missions, chassis, professions, skills, PVP, and repair
- **[AWS_HOSTING.md](AWS_HOSTING.md)** — Step-by-step guide to host on AWS (~$0-10/month)
