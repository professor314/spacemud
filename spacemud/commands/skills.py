"""
Skill commands — ``use`` and ``skills``.

``use <skill>`` activates a skill (checks access, cooldown, power).
``skills`` lists all available skills with their cooldown status.
"""

from evennia.commands.command import Command

from world.skills import SKILLS
from utils.skills import is_skill_ready, set_cooldown, remaining_cooldown, apply_skill_effect


class CmdUse(Command):
    """
    Activate a skill.

    Usage:
      use <skill name>

    Examples:
      use quick scan
      use upload virus
    """

    key = "use"
    help_category = "Skills"

    def func(self):
        if not self.args:
            self.caller.msg("Usage: use <skill name>")
            return

        # Normalise input to a skill_id
        skill_id = self.args.strip().lower().replace(" ", "_")

        skill = SKILLS.get(skill_id)
        if not skill:
            self.caller.msg("Unknown skill.")
            return

        # Access check — generic skills are available to everyone;
        # profession skills require the skill to be in db.skills.
        if not skill["generic"]:
            unlocked = self.caller.db.skills or []
            if skill_id not in unlocked:
                self.caller.msg("Skill not unlocked.")
                return

        # Cooldown check
        if not is_skill_ready(self.caller, skill_id):
            remaining = remaining_cooldown(self.caller, skill_id)
            self.caller.msg(f"Skill on cooldown. Ready in {remaining}s.")
            return

        # Power check
        power_cost = skill["power_cost"]
        if self.caller.db.power < power_cost:
            self.caller.msg(f"Insufficient power. Need {power_cost}.")
            return

        # Deduct power, set cooldown, apply effect
        self.caller.db.power -= power_cost
        set_cooldown(self.caller, skill_id, skill["cooldown"])
        apply_skill_effect(self.caller, skill)


class CmdSkills(Command):
    """
    List all available skills and their cooldown status.

    Usage:
      skills
    """

    key = "skills"
    help_category = "Skills"

    def func(self):
        unlocked = self.caller.db.skills or []
        lines = ["|wAvailable Skills:|n"]

        for skill_id, skill in SKILLS.items():
            # Show generic skills and any unlocked profession skills
            if not skill["generic"] and skill_id not in unlocked:
                continue

            if is_skill_ready(self.caller, skill_id):
                status = "|gREADY|n"
            else:
                remaining = remaining_cooldown(self.caller, skill_id)
                status = f"|rCooldown: {remaining}s|n"

            lines.append(
                f"  {skill['name']} (power: {skill['power_cost']}) — {status}"
            )

        if len(lines) == 1:
            lines.append("  No skills available.")

        self.caller.msg("\n".join(lines))
