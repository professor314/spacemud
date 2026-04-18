"""
RobotCmdSet — the default command set for all robot universe characters.

Inherits from Evennia's default CharacterCmdSet so all built-in commands
(look, teleport, @py, @batchcode, movement, etc.) are preserved. Our
custom commands are added on top and override any defaults with the same key.
"""

from evennia import default_cmds

from commands.combat import CmdAttack, CmdFlee
from commands.items import CmdGet, CmdDrop, CmdInventory, CmdEquip
from commands.missions import CmdTalk, CmdComplete, CmdMissions, CmdAccept
from commands.general import CmdStatus, CmdRepair, CmdScan, CmdHelp
from commands.chassis import CmdSelect, CmdChassisInfo, CmdProfessionInfo


class RobotCmdSet(default_cmds.CharacterCmdSet):
    """
    The default CmdSet for robot universe characters. Extends Evennia's built-in
    CharacterCmdSet so all default commands (look, go, teleport, @py, etc.)
    remain available. Custom robot commands are added on top.
    """

    key = "DefaultCharacter"

    def at_cmdset_creation(self):
        # Load all Evennia defaults first (look, go, teleport, @batchcode, etc.)
        super().at_cmdset_creation()

        # Combat
        self.add(CmdAttack())
        self.add(CmdFlee())
        # Items
        self.add(CmdGet())
        self.add(CmdDrop())
        self.add(CmdInventory())
        self.add(CmdEquip())
        # Missions
        self.add(CmdTalk())
        self.add(CmdComplete())
        self.add(CmdMissions())
        self.add(CmdAccept())
        # General
        self.add(CmdStatus())
        self.add(CmdRepair())
        self.add(CmdScan())
        self.add(CmdHelp())
        # Chassis / Profession
        self.add(CmdSelect())
        self.add(CmdChassisInfo())
        self.add(CmdProfessionInfo())
