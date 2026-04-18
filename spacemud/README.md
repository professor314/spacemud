# Space MUD — Setup Guide

A text-based multiplayer game set on a derelict space station. You are a robot. You don't know that yet. Built on [Evennia](https://www.evennia.com/).

---

## Requirements

- Python 3.10+
- Evennia 6.0.0

Install dependencies:

```powershell
pip install -r requirements.txt
```

---

## First-Time Setup

Open PowerShell and navigate to the game directory:

```powershell
cd "path/to/Space MUD/spacemud"
```

Run the database migration:

```powershell
evennia migrate
```

Start the server:

```powershell
evennia start
```

The first time you start, Evennia will ask you to create a superuser account. Pick a name and password (at least 8 characters, not a common word).

---

## Connecting

Open your browser to:

```
http://localhost:4001
```

That's the built-in web client. No telnet needed.

---

## Loading the World (First Time Only)

The world content (rooms, NPCs, artifacts, hostiles) must be loaded once after the server first starts.

Open a **second** terminal window (keep the server running), navigate to the game directory, and run:

```powershell
python manage.py shell
```

Wait for the `>>>` prompt, then type these lines one at a time:

```python
import evennia
evennia._init()
from world.batch_code import main
main(type('C', (), {'msg': staticmethod(print)})())
```

You should see:

```
World content created successfully!
  Central Station: 8 rooms
  Outer Zone: 7 rooms
  ...
```

Type `exit()` to close the shell. You only need to do this once — the world is saved to the database.

---

## Reloading After Code Changes

If you make changes to any Python files, reload the server without disconnecting players:

```powershell
cd "path/to/Space MUD/spacemud"
evennia reload
```

**Important:** You must be inside the `spacemud` directory when running any `evennia` command. If you get an error about `server\conf\settings.py`, it means you're in the wrong directory.

---

## Stopping the Server

```powershell
cd "path/to/Space MUD/spacemud"
evennia stop
```

---

## Running the Tests

```powershell
cd spacemud
python -m pytest tests/ -v
```

---

## Other Docs

- **[HOW_TO_PLAY.md](HOW_TO_PLAY.md)** — Player guide with commands, map, and missions
- **[AWS_HOSTING.md](AWS_HOSTING.md)** — How to host this game on AWS
