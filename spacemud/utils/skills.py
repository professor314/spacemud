"""
Skill utility functions — cooldown tracking and effect application.

Provides helpers used by the ``use`` command to check readiness,
set cooldowns, and apply the mechanical effect of each skill.
"""

import time


def is_skill_ready(character, skill_id):
    """Return True if the skill's cooldown has expired (or was never set)."""
    cooldowns = character.db.skill_cooldowns or {}
    ready_at = cooldowns.get(skill_id, 0)
    return time.time() >= ready_at


def set_cooldown(character, skill_id, duration):
    """Record a cooldown expiry timestamp for *skill_id* on *character*."""
    cooldowns = character.db.skill_cooldowns or {}
    cooldowns[skill_id] = time.time() + duration
    character.db.skill_cooldowns = cooldowns


def remaining_cooldown(character, skill_id):
    """Return whole seconds remaining on *skill_id*'s cooldown (0 if ready)."""
    cooldowns = character.db.skill_cooldowns or {}
    ready_at = cooldowns.get(skill_id, 0)
    remaining = ready_at - time.time()
    return max(0, int(remaining))


def apply_skill_effect(character, skill):
    """
    Apply the mechanical effect described by *skill* dict to *character*.

    Supported effect types:
      direct_damage  — deal damage to current combat target
      heal           — restore integrity (capped at max)
      bonus_damage   — add to next attack's damage
      reveal_stats   — display target's stats
      restore_power  — restore power (capped at max)
      noop           — placeholder, no mechanical effect
    """
    effect = skill["effect"]
    value = skill["effect_value"]

    if effect == "direct_damage":
        # Find current combat target
        for script in character.scripts.all():
            if script.key == "combat_script":
                target = script.db.defender
                if target:
                    target.db.integrity -= value
                    character.msg(f"Skill applied. {value} damage dealt to {target.name}.")
                    if target.db.integrity <= 0:
                        target.at_death(character)
                return
        character.msg("No target. Must be in combat.")

    elif effect == "heal":
        character.db.integrity = min(
            character.db.integrity + value,
            character.db.max_integrity,
        )
        character.msg(f"Integrity restored. Current: {character.db.integrity}.")

    elif effect == "bonus_damage":
        character.db.bonus_damage = (character.db.bonus_damage or 0) + value
        character.msg(f"Next attack boosted by {value}.")

    elif effect == "reveal_stats":
        for script in character.scripts.all():
            if script.key == "combat_script":
                target = script.db.defender
                if target:
                    character.msg(
                        f"Target: {target.name}. "
                        f"Integrity: {target.db.integrity}/{target.db.max_integrity}. "
                        f"Processing: {target.db.processing}. Shielding: {target.db.shielding}."
                    )
                return
        character.msg("No target. Must be in combat.")

    elif effect == "restore_power":
        character.db.power = min(
            character.db.power + value,
            character.db.max_power,
        )
        character.msg(f"Power restored. Current: {character.db.power}.")

    elif effect == "noop":
        character.msg(f"Skill activated: {skill['name']}. No effect implemented yet.")
