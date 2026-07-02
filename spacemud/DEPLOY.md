# Deploying Changes to Space MUD

## Quick Deploy (code changes)

From your local machine, after committing and pushing to GitHub:

```powershell
# 1. Push your changes
git push origin main

# 2. SSH in and pull
ssh -i ~/.ssh/space-mud-key.pem ubuntu@44.198.208.85 "cd ~/spacemud && git pull origin main"

# 3. Reload (no disconnect for players)
ssh -i ~/.ssh/space-mud-key.pem ubuntu@44.198.208.85 "source ~/mudenv/bin/activate && cd ~/spacemud/spacemud && evennia reload"
```

Players may need to disconnect and reconnect to see typeclass or command changes.

## World Data Changes (rooms, NPCs, items)

If you changed JSON files in `world/data/`, you need to reset the world:

```powershell
# SSH in
ssh -i ~/.ssh/space-mud-key.pem ubuntu@44.198.208.85

# On the server:
source ~/mudenv/bin/activate
cd ~/spacemud/spacemud
python manage.py reset_world --confirm
evennia reload
```

**Warning:** This deletes all world objects and recreates them from JSON. Player accounts and characters are preserved, but characters will be moved to the starting room.

If `reset_world` has issues, the nuclear option is:

```bash
evennia stop
rm server/evennia.db3
evennia migrate
evennia start
# Then load world (see below)
```

This wipes everything including accounts — players must recreate characters.

## Loading World Data (fresh database)

After a fresh database, create the superuser and load the world:

```bash
# Create admin account
python -c "
import os, sys, django
sys.path.insert(0, '.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.conf.settings')
django.setup()
from django.contrib.auth import get_user_model
User = get_user_model()
User.objects.create_superuser('admin', 'admin@localhost', 'YOUR_PASSWORD')
"

# Start server
evennia start

# Load world
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
"

# Reload
evennia reload
```

## Server Management

```bash
# Check status
ssh -i ~/.ssh/space-mud-key.pem ubuntu@44.198.208.85 "source ~/mudenv/bin/activate && cd ~/spacemud/spacemud && evennia status"

# Stop
ssh -i ~/.ssh/space-mud-key.pem ubuntu@44.198.208.85 "source ~/mudenv/bin/activate && cd ~/spacemud/spacemud && evennia stop"

# Start
ssh -i ~/.ssh/space-mud-key.pem ubuntu@44.198.208.85 "source ~/mudenv/bin/activate && cd ~/spacemud/spacemud && evennia start"

# View logs
ssh -i ~/.ssh/space-mud-key.pem ubuntu@44.198.208.85 "tail -50 ~/spacemud/spacemud/server/logs/server.log"
```

## Server Details

- **IP:** 44.198.208.85
- **Web client:** http://play.imadestuff.com:4001
- **Telnet:** play.imadestuff.com:4000
- **SSH:** `ssh -i ~/.ssh/space-mud-key.pem ubuntu@44.198.208.85`
- **Instance:** i-0860a3721aa909e77 (us-east-1)
- **Auto-restart:** systemd service `spacemud` (enabled)
- **Idle timeout:** 30 minutes
