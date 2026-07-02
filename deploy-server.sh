#!/bin/bash
set -euo pipefail

# Space MUD — Server Deploy Script
# Run this on the EC2 server after pushing changes to GitHub.
# Usage: ./deploy.sh [--reset-world]
#
# Without flags: pulls code, runs migrations, reloads server.
# With --reset-world: also wipes and rebuilds all rooms/NPCs/items from JSON.

GAME_DIR="$HOME/spacemud/spacemud"
VENV="$HOME/mudenv/bin/activate"

source "$VENV"
cd "$HOME/spacemud"

echo "=== Pulling latest from GitHub ==="
git pull origin main

cd "$GAME_DIR"

echo "=== Running migrations ==="
evennia migrate 2>&1 | tail -3

echo "=== Reloading server ==="
evennia reload

# If --reset-world flag is passed, reload world data from JSON
if [[ "${1:-}" == "--reset-world" ]]; then
    echo "=== Resetting world data from JSON ==="
    python << 'PYEOF'
import os, sys, django
sys.path.insert(0, '.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.conf.settings')
django.setup()
import evennia
evennia._init()
from evennia.objects.models import ObjectDB

# Delete existing world objects (not characters/accounts)
world_types = [
    'typeclasses.rooms.StationRoom',
    'typeclasses.exits.Exit',
    'evennia.objects.objects.DefaultExit',
    'typeclasses.objects.Artifact',
    'typeclasses.objects.Equipment',
    'typeclasses.objects.NPC',
    'typeclasses.objects.Hostile',
    'typeclasses.objects.RepairableObject',
]
deleted = 0
for obj in ObjectDB.objects.all():
    if obj.db_typeclass_path in world_types:
        try:
            obj.delete()
            deleted += 1
        except Exception:
            pass
print(f'  Deleted {deleted} world objects.')

from world.batch_code import main
class C:
    @staticmethod
    def msg(text):
        print(f'  {text}')
main(C())

# Move all characters to Main Corridor
mc = ObjectDB.objects.filter(db_key='Main Corridor').first()
if mc:
    for char in ObjectDB.objects.filter(db_typeclass_path='typeclasses.characters.RobotCharacter'):
        char.move_to(mc, quiet=True)
    print('  Characters moved to Main Corridor.')
else:
    print('  WARNING: Main Corridor not found!')
PYEOF

    echo "=== Reloading server after world reset ==="
    evennia reload
fi

echo ""
echo "=== Deploy complete ==="
evennia status
