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

### Station Restore
1. `talk Maintenance Unit 7` (Main Corridor)
2. `accept station_restore`
3. Repair any 2 damaged station systems
4. Return to Maintenance Unit 7 and `complete Station Restore`
5. Reward: 250 XP, 125 credits

### Clear the Wreck
1. `talk Damaged Scout` (Docking Port)
2. `accept clear_the_wreck`
3. Destroy 2 Corrupted Sentries and 1 Rogue Program in the Outer Zone
4. Return to Damaged Scout and `complete Clear the Wreck`
5. Reward: 300 XP, 150 credits

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
- Some repairs require other repairs first — check the Prerequisite column. If the prerequisite is not repaired, the repair is blocked.

### Repairable Objects

| Object | Location | Repair Level | Cost | Prerequisite |
|---|---|---|---|---|
| Emergency Lighting | Main Corridor | 1 | 1x Power Cell | — |
| Reactor Coupling | Reactor Terminal | 2 | 2x Power Cell + 1x Circuit Component | — |
| Sensor Array | Observation Deck | 2 | 1x Circuit Component | Emergency Lighting |
| Airlock Seal | Airlock | 3 | 2x Circuit Component + 1x Power Cell | — |
| Communications Relay | Communications Array | 3 | 1x Data Chip + 2x Circuit Component | Sensor Array |

---

## Chassis System

Chassis Terminal located in Repair Bay. Approach it and select your frame. One-time selection. No take-backs.

```
select <chassis>
```

View your current chassis:

```
chassis
```

If no chassis installed, output reads: `bare circuit board`.

### Available Chassis

| Chassis | Stat Modifiers | Passive |
|---|---|---|
| **Scout Unit** | processing +3, shielding -1, max_power +10 | `enhanced_sensors` — sensor range extended. Room scan shows exits of adjacent rooms. |
| **Heavy Unit** | max_integrity +30, shielding +3, processing -2 | `damage_reduction` — physical damage reduced by 2 per hit (minimum 1). |
| **Repair Unit** | repair_level +2, max_integrity +10 | `self_repair` — regenerates 1 integrity per minute when not in combat. |
| **Infiltrator Unit** | processing +2, max_power +15 | `reduced_detection` — hostile entities are less likely to notice you. |
| **Broadcast Unit** | max_power +10, max_integrity +10 | `cross_zone_comms` — can transmit messages to other units in any zone. |

---

## Professions System

Protocol Terminal located in Data Core. Requires chassis installed and level 3 or higher. One-time selection.

```
select <profession>
```

View your current profession:

```
profession
```

If no profession installed, output reads: `No protocol installed.`

### Available Professions

| Profession | Growth per Level | Skills |
|---|---|---|
| **Combat Protocol** | integrity +5, processing +2, shielding +1, power +3 | `upload_virus` (level 3), `overclock` (level 5) |
| **Systems Engineer** | integrity +8, processing +1, shielding +1, repair_level +1, power +5 | `emergency_patch` (level 3), `diagnostic_scan` (level 5) |
| **Infiltration Protocol** | integrity +5, processing +1, shielding +1, power +8 | `hack_console` (level 3), `stealth_mode` (level 5) |
| **Broadcast Protocol** | integrity +7, processing +1, shielding +1, power +6 | `signal_boost` (level 3), `power_surge` (level 5) |

---

## Skills

Activate a skill:

```
use <skill>
```

List available skills and cooldown status:

```
skills
```

Skills cost power. Skills have cooldowns. Insufficient power or active cooldown = rejected.

### Generic Skills (all units)

| Skill | Power Cost | Cooldown | Effect |
|---|---|---|---|
| `quick_scan` | 10 | 30s | Next attack deals +5 damage. |
| `emergency_reboot` | 15 | 60s | Restore 20 integrity. Out of combat only. |

Profession skills unlock at specific levels (see Professions table above). Only available if your profession grants them.

---

## PVP

Debris Drift is a PVP zone. Player-versus-player combat enabled there only.

```
attack <player>
```

Outside PVP zones: `Combat protocol restricted in this zone.`

On PVP death: emergency reboot to Repair Bay at 25% integrity. 10% XP penalty applied. No inventory transfer.

---

## Unit States

Your unit has an operational state. It affects what commands are available.

| State | How it triggers | Restrictions |
|---|---|---|
| **active** | Default state. Any command from idle returns here. | None. |
| **idle** | Type `idle` or `idle <message>`. Broadcasts to room. | None — any command returns you to active. |
| **combat** | Entering combat via `attack`. | `repair`, `missions`, `complete`, `talk`, `select` blocked. `attack`, `flee`, `use`, `status` allowed. |
| **offline** | Integrity reaches 0. | All commands blocked except `scan`/`look`/`help`. Transitions to active on reboot to Repair Bay. |

```
idle
idle Recharging.
```

---

## Tips

- Hostiles respawn after 90–150 seconds. You can farm them for XP and salvage.
- Your state (location, inventory, missions, stats) saves automatically.
- If you disconnect and reconnect, everything is exactly where you left it.
- Use `status` often to check your integrity before entering hostile areas.
