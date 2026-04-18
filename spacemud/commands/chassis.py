"""
Chassis and profession commands: select, chassis, profession.
"""

from evennia.commands.command import Command


class CmdSelect(Command):
    """
    Select a chassis or profession at a terminal.

    Usage:
      select <id>

    Must be near a Chassis Terminal or Protocol Terminal NPC.
    At a Chassis Terminal, installs the specified chassis.
    At a Protocol Terminal, installs the specified profession.
    """

    key = "select"
    help_category = "General"

    def func(self):
        if not self.args:
            self.caller.msg("Select what? Usage: select <id>")
            return

        selection = self.args.strip().lower()

        # Search room contents for terminal NPCs
        chassis_terminal = None
        protocol_terminal = None
        if self.caller.location:
            for obj in self.caller.location.contents:
                role = obj.db.role
                if role == "chassis_terminal":
                    chassis_terminal = obj
                elif role == "protocol_terminal":
                    protocol_terminal = obj

        if chassis_terminal:
            self.caller.install_chassis(selection)
        elif protocol_terminal:
            self.caller.install_profession(selection)
        else:
            self.caller.msg("No terminal detected.")


class CmdChassisInfo(Command):
    """
    Display your current chassis information.

    Usage:
      chassis

    Shows chassis name, description, and passive ability.
    If no chassis is installed, reports bare circuit board status.
    """

    key = "chassis"
    help_category = "General"

    def func(self):
        chassis_id = self.caller.db.chassis
        if not chassis_id:
            self.caller.msg("No chassis installed. Unit is bare circuit board.")
            return

        from world.chassis import CHASSIS

        chassis = CHASSIS.get(chassis_id)
        if not chassis:
            self.caller.msg(f"Chassis '{chassis_id}' not found in database.")
            return

        self.caller.msg(
            f"|wChassis:|n {chassis['name']}\n"
            f"|wDescription:|n {chassis['description']}\n"
            f"|wPassive:|n {chassis['passive_description']}"
        )


class CmdProfessionInfo(Command):
    """
    Display your current profession information.

    Usage:
      profession
      protocol

    Shows profession name, description, growth table, and skills.
    If no profession is installed, reports no protocol status.
    """

    key = "profession"
    aliases = ["protocol"]
    help_category = "General"

    def func(self):
        profession_id = self.caller.db.profession
        if not profession_id:
            self.caller.msg("No protocol installed.")
            return

        try:
            from world.professions import PROFESSIONS
        except ImportError:
            self.caller.msg("Profession system not yet available.")
            return

        prof = PROFESSIONS.get(profession_id)
        if not prof:
            self.caller.msg(f"Protocol '{profession_id}' not found in database.")
            return

        # Format growth table
        growth_lines = ", ".join(
            f"{stat}: +{value}" for stat, value in prof.get("growth", {}).items()
        )

        # Format skills
        skills = prof.get("skills", {})
        if skills:
            skill_lines = ", ".join(
                f"Lv{level}: {skill_id}" for level, skill_id in skills.items()
            )
        else:
            skill_lines = "None"

        self.caller.msg(
            f"|wProtocol:|n {prof['name']}\n"
            f"|wDescription:|n {prof['description']}\n"
            f"|wGrowth per level:|n {growth_lines}\n"
            f"|wSkills:|n {skill_lines}"
        )
