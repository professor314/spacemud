r"""
Evennia settings file.

The available options are found in the default settings file found
here:

https://www.evennia.com/docs/latest/Setup/Settings-Default.html

Remember:

Don't copy more from the default file than you actually intend to
change; this will make sure that you don't overload upstream updates
unnecessarily.

When changing a setting requiring a file system path (like
path/to/actual/file.py), use GAME_DIR and EVENNIA_DIR to reference
your game folder and the Evennia library folders respectively. Python
paths (path.to.module) should be given relative to the game's root
folder (typeclasses.foo) whereas paths within the Evennia library
needs to be given explicitly (evennia.foo).

If you want to share your game dir, including its settings, you can
put secret game- or server-specific settings in secret_settings.py.

"""

# Use the defaults from Evennia unless explicitly overridden
from evennia.settings_default import *

######################################################################
# Evennia base server config
######################################################################

# This is the name of your game. Make it catchy!
SERVERNAME = "spacemud"


######################################################################
# Settings given in secret_settings.py override those in this file.
######################################################################
try:
    from server.conf.secret_settings import *
except ImportError:
    print("secret_settings.py file not found or failed to import.")

######################################################################
# Robot Universe MUD Custom Settings
######################################################################

# Custom typeclass paths
BASE_CHARACTER_TYPECLASS = "typeclasses.characters.RobotCharacter"
BASE_ROOM_TYPECLASS = "typeclasses.rooms.StationRoom"
BASE_OBJECT_TYPECLASS = "typeclasses.objects.Artifact"
BASE_SCRIPT_TYPECLASS = "typeclasses.scripts.DefaultScript"
BASE_EXIT_TYPECLASS = "typeclasses.exits.Exit"  # keep default exit

# Default character CmdSet
CMDSET_CHARACTER = "commands.cmdsets.RobotCmdSet"

# Register utils app so Django discovers the validate_world management command
INSTALLED_APPS += ["utils"]

# Robot universe connection screen (welcome banner)
CONNECTION_SCREEN_MODULE = "server.conf.connection_screens"

# Robot universe unlogged-in command set (login prompts)
CMDSET_UNLOGGEDIN = "commands.unloggedin.RobotUnloggedinCmdSet"

######################################################################
# Session & Idle Settings
######################################################################

# Kick idle players after 30 minutes (1800 seconds)
IDLE_TIMEOUT = 1800

# Message shown to the player when they're about to be kicked (60s warning)
IDLE_TIMEOUT_WARNING = 60

# Message shown when disconnected for idle
IDLE_DISCONNECT_MSG = "\n|rSession terminated. Unit inactive for 30 minutes.|n\nReconnect with: connect <unit_designation> <access_key>\n"

######################################################################
# Network — Allow external connections (required for public hosting)
######################################################################
TELNET_INTERFACES = ["0.0.0.0"]
WEBSERVER_INTERFACES = ["0.0.0.0"]
WEBSOCKET_CLIENT_INTERFACE = "0.0.0.0"

# New characters spawn in Main Corridor, not Limbo
START_LOCATION = '#3'
DEFAULT_HOME = '#3'
