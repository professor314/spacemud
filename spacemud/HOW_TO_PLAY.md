# Space MUD — How to Play

You wake up. You remember nothing. A terminal blinks in front of you.

---

## Creating Your Unit

At the boot screen, type:

```
create <name> <password>
```

Example:
```
create Echo station99x
```

Password must be at least 8 characters and not a common word. After creation, connect:

```
connect Echo station99x
```

You'll see: `I remember my name. Echo. But that's all I know.`

---

## First Steps

You start in Limbo. Teleport to the station:

```
teleport Main Corridor
```

Then type `scan` or `look` to see where you are.

---

## Commands

| Command | What it does |
|---|---|
| `scan` or `look` | Describe current room |
| `north` / `south` / `east` / `west` | Move between rooms |
| `status` | View your stats (integrity, power, processing, shielding, repair level) |
| `inventory` | List artifacts you're carrying |
| `get <item>` | Pick up an artifact |
| `equip <item>` or `install <item>` | Install a component (applies stat modifiers) |
| `drop <item>` | Drop an artifact |
| `attack <hostile>` | Engage a hostile in combat |
| `flee` | Disengage from combat |
| `talk <npc>` | Talk to another unit |
| `accept <mission_id>` | Accept a mission |
| `missions` | View your mission log |
| `complete <mission title>` | Turn in a completed mission |
| `repair <object>` | Repair a damaged station system |
| `help` | List all available commands |
| `help <command>` | Detailed help for a specific command |

---

## The Station Map

### Central Station (starting zone)

Starting from **Main Corridor**:

| Direction | Destination | What's there |
|---|---|---|
| east | Storage Hub | Power Cells |
| west | Repair Bay | Where you reboot if destroyed |
| north | Reactor Terminal | Power Cells, Reactor Coupling (repairable) |
| south | Observation Deck | — |
| north from Storage Hub | Maintenance Shaft | — |
| south from Observation Deck | Data Core | Data Chip, Idle Terminal (NPC) |
| east from Reactor Terminal | Docking Port | Damaged Scout (NPC, mission giver) |

**NPCs in Central Station:**
- **Maintenance Unit 7** (Main Corridor) — offers Boot Sequence and Signal Search missions
- **Damaged Scout** (Docking Port) — offers Salvage Run mission
- **Idle Terminal** (Data Core) — displays fragmented station logs

### Outer Zone (damaged, hostile)

From **Docking Port**, go west to enter the Outer Zone:

| Direction | Destination | What's there |
|---|---|---|
| west from Docking Port | Collapsed Corridor | Entry to outer zone |
| north from Collapsed Corridor | Breached Lab | Haywire Drone, Overclocked Processor |
| south from Collapsed Corridor | Cargo Wreck | Corrupted Sentry, Reinforced Plating |
| east from Collapsed Corridor | Crew Remnants | — |
| north from Breached Lab | Communications Array | Needed for Signal Search mission |
| south from Cargo Wreck | Debris Drift | Rogue Program |
| north from Crew Remnants | Airlock | — |

**Hostiles:**
- **Corrupted Sentry** (Cargo Wreck) — processing 12, shielding 4, 60 integrity. Drops Circuit Component.
- **Haywire Drone** (Breached Lab) — processing 8, shielding 6, 40 integrity.
- **Rogue Program** (Debris Drift) — processing 15, shielding 2, 50 integrity.

---

## Stats

| Stat | What it means |
|---|---|
| **Integrity** | Your structural condition. Reaches 0 = emergency reboot to Repair Bay at 25%. |
| **Power** | Energy for skills and software repairs. |
| **Processing** | Your offensive output in combat. |
| **Shielding** | Your defensive resistance in combat. |
| **Repair Level** | Determines what station systems you can repair. |
| **Credits** | Currency earned from missions. |

---

## Combat

Type `attack <hostile name>` to engage. Combat runs automatically in 2-second rounds:

```
Processing output: 8. Target integrity reduced. Target integrity: 52.
Impact detected. Integrity reduced by 5. Current integrity: 95.
```

If your integrity reaches 0:
```
Critical failure. Emergency reboot initiated. Repair Bay.
```

You wake up in the Repair Bay at 25% integrity.

Type `flee` to disengage and move to a random adjacent room.

---

## Missions

### Boot Sequence
1. `talk Maintenance Unit 7` (Main Corridor)
2. `accept boot_sequence`
3. Collect 3 Power Cells (found in Storage Hub and Reactor Terminal area)
4. Return to Maintenance Unit 7 and `complete Boot Sequence`
5. Reward: 300 XP, 150 credits

### Signal Search
1. `talk Maintenance Unit 7` (Main Corridor)
2. `accept signal_search`
3. Navigate to the Communications Array in the Outer Zone
4. Return to Maintenance Unit 7 and `complete Signal Search`
5. Reward: 200 XP, 100 credits

### Salvage Run
1. `talk Damaged Scout` (Docking Port)
2. `accept salvage_run`
3. Collect 2 Circuit Components (dropped by Corrupted Sentry in Cargo Wreck)
4. Return to Damaged Scout and `complete Salvage Run`
5. Reward: 150 XP, 75 credits

---

## Repairing the Station

Some objects in the station are damaged and can be repaired. To see what's repairable, look for `[DAMAGED]` tags when you scan a room.

```
repair Emergency Lighting
```

Requirements:
- Your **repair level** must meet or exceed the object's required level
- You must have the required **components** in your inventory (consumed on repair)
- Some repairs cost **power** instead of components (software repairs)

### Repairable Objects (Phase 1)

| Object | Location | Repair Level | Cost |
|---|---|---|---|
| Emergency Lighting | Main Corridor | 1 | 1x Power Cell |
| Reactor Coupling | Reactor Terminal | 2 | 2x Power Cell + 1x Circuit Component |

---

## Tips

- Hostiles respawn after 90–150 seconds. You can farm them for XP and salvage.
- Your state (location, inventory, missions, stats) saves automatically.
- If you disconnect and reconnect, everything is exactly where you left it.
- Use `status` often to check your integrity before entering hostile areas.
