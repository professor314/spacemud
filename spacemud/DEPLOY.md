# Deploying Changes to Space MUD

## One-Command Deploy

After committing your changes:

```powershell
# Code changes only (Python, commands, settings)
.\deploy.ps1

# World data changes (rooms.json, npcs.json, exits.json, etc.)
.\deploy.ps1 -ResetWorld
```

That's it. The script pushes to GitHub, SSHs into the server, pulls, runs migrations, and reloads. With `-ResetWorld`, it also wipes and rebuilds all rooms/NPCs/items from JSON (characters are preserved and moved to Main Corridor).

## When to use -ResetWorld

Use it when you've changed any file in `world/data/`:
- `rooms.json` (room descriptions, new rooms)
- `exits.json` (connections between rooms)
- `npcs.json`, `hostiles.json`, `artifacts.json`, `repairables.json`

Don't use it for Python code changes (commands, typeclasses, settings) — a regular deploy handles those with just a reload.

## What each deploy does

**Regular deploy (`.\deploy.ps1`):**
1. `git push origin main` (your machine)
2. `git pull origin main` (server)
3. `evennia migrate` (apply any database changes)
4. `evennia reload` (hot-reload code without disconnecting players)

**World reset deploy (`.\deploy.ps1 -ResetWorld`):**
1–4. Same as above, plus:
5. Deletes all world objects (rooms, exits, NPCs, items, hostiles)
6. Recreates everything from JSON files
7. Moves all player characters to Main Corridor
8. Reloads server again

## Manual Server Access

```powershell
# SSH in
ssh -i ~/.ssh/space-mud-key.pem ubuntu@44.198.208.85

# On the server:
source ~/mudenv/bin/activate
cd ~/spacemud/spacemud

# Commands:
evennia status        # Check if running
evennia reload        # Hot-reload code
evennia stop          # Stop server
evennia start         # Start server
evennia migrate       # Run database migrations

# Logs:
tail -50 server/logs/server.log
tail -50 server/logs/portal.log
```

## Server Details

| Item | Value |
|------|-------|
| IP | 44.198.208.85 |
| Web client | http://play.imadestuff.com:4001 |
| Telnet | play.imadestuff.com:4000 |
| SSH | `ssh -i ~/.ssh/space-mud-key.pem ubuntu@44.198.208.85` |
| Instance | i-0860a3721aa909e77 (us-east-1) |
| Auto-restart | systemd service `spacemud` (enabled) |
| Idle timeout | 30 minutes |
| Deploy script (server) | `~/spacemud/deploy.sh` |
| Deploy script (local) | `space-mud/deploy.ps1` |

## Troubleshooting

**Players land in Limbo after deploy:**
- Run `.\deploy.ps1 -ResetWorld` to rebuild world and move characters.

**Server won't start:**
- SSH in and check logs: `tail server/logs/server.log`
- Common cause: syntax error in settings.py. Fix and `evennia start`.

**"Permission denied" on SSH:**
- Your home IP may have changed. Update the Security Group SSH rule in AWS Console (EC2 → Security Groups → `space-mud-sg` → Edit inbound rules → update SSH source IP).

**Out of memory:**
- Swap should handle it (1 GB configured). If still OOMs: `sudo fallocate -l 2G /swapfile` to double it.

**Need a completely fresh start:**
```bash
evennia stop
rm server/evennia.db3
evennia migrate
evennia start
# Then create superuser and load world — see below
```

After a fresh DB, create the admin account:
```bash
python -c "
import os, sys, django
sys.path.insert(0, '.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.conf.settings')
django.setup()
from django.contrib.auth import get_user_model
User = get_user_model()
User.objects.create_superuser('admin', 'admin@localhost', 'YOUR_PASSWORD')
print('Admin created')
"
```

Then load the world:
```bash
python -c "
import os, sys, django
sys.path.insert(0, '.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.conf.settings')
django.setup()
import evennia; evennia._init()
from world.batch_code import main
class C:
    @staticmethod
    def msg(text): print(text)
main(C())
print('World loaded')
"
evennia reload
```
