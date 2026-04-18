"""
Unlogged-in command set with robot universe prompts.

Overrides Evennia's default CmdUnconnectedConnect and CmdUnconnectedCreate
commands to use robot-voice terminology:
  - "Unit designation:" instead of "Username:"
  - "Access key:" instead of "Password:"
  - Terse robot-voice error and confirmation messages.

The RobotUnloggedinCmdSet is registered in settings.py via
CMDSET_UNLOGGEDIN so Evennia uses it instead of the default.
"""

import re

from django.conf import settings

from evennia import CmdSet
from evennia.commands.default.unloggedin import (
    CmdUnconnectedCreate as _DefaultCreate,
    CmdUnconnectedConnect as _DefaultConnect,
    CmdUnconnectedEncoding,
    CmdUnconnectedHelp,
    CmdUnconnectedInfo,
    CmdUnconnectedLook,
    CmdUnconnectedQuit,
    CmdUnconnectedScreenreader,
)
from evennia.utils import class_from_module


class CmdUnconnectedConnect(_DefaultConnect):
    """
    Connect to the station network.

    Usage (at login screen):
        connect <unit_designation> <access_key>
        connect "unit designation" "access key"

    Use the |wcreate|n command to initialise a new unit first.
    If your designation contains spaces, enclose it in double quotes.
    """

    key = "connect"
    aliases = ["conn", "con", "co"]
    locks = "cmd:all()"
    arg_regex = r"\s.*?|$"

    def func(self):
        """
        Authenticate the unit. Uses robot-voice terminology in all
        messages while delegating actual auth logic to Evennia's Account
        typeclass (same as the default command).
        """
        session = self.caller
        address = session.address
        args = self.args

        # Extract double-quoted parts (handles names/access keys with spaces)
        parts = [part.strip() for part in re.split(r'"', args) if part.strip()]
        if len(parts) == 1:
            parts = parts[0].split(None, 1)

            # Guest login
            if len(parts) == 1 and parts[0].lower() == "guest":
                Guest = class_from_module(settings.BASE_GUEST_TYPECLASS)
                account, errors = Guest.authenticate(ip=address)
                if account:
                    session.sessionhandler.login(session, account)
                    return
                else:
                    session.msg("|R%s|n" % "\n".join(errors))
                    return

        if len(parts) != 2:
            session.msg(
                "\n\r |wUsage:|n  connect <unit_designation> <access_key>"
            )
            return

        Account = class_from_module(settings.BASE_ACCOUNT_TYPECLASS)
        name, password = parts
        account, errors = Account.authenticate(
            username=name, password=password, ip=address, session=session
        )
        if account:
            session.sessionhandler.login(session, account)
        else:
            session.msg(
                "|RAuthentication failed.|n\n"
                + "|R%s|n" % "\n".join(errors)
            )


class CmdUnconnectedCreate(_DefaultCreate):
    """
    Initialise a new unit on the station network.

    Usage (at login screen):
        create <unit_designation> <access_key>
        create "unit designation" "access key"

    This registers a new unit.
    If your designation contains spaces, enclose it in double quotes.
    Access keys must be at least 8 characters.
    """

    key = "create"
    aliases = ["cre", "cr"]
    locks = "cmd:all()"
    arg_regex = r"\s.*?|$"

    def at_pre_cmd(self):
        """Verify that unit creation is enabled."""
        if not settings.NEW_ACCOUNT_REGISTRATION_ENABLED:
            self.msg(
                "|RUnit registration suspended.|n"
            )
            return True  # truthy return cancels the command
        return super().at_pre_cmd()

    def func(self):
        """Register a new unit with robot-voice prompts."""
        session = self.caller
        args = self.args.strip()
        address = session.address

        Account = class_from_module(settings.BASE_ACCOUNT_TYPECLASS)

        # Extract double-quoted parts
        parts = [part.strip() for part in re.split(r'"', args) if part.strip()]
        if len(parts) == 1:
            parts = parts[0].split(None, 1)

        if len(parts) != 2:
            session.msg(
                "\n |wUsage:|n  create <unit_designation> <access_key>"
                "\nIf your designation or access key contains spaces, "
                "enclose it in double quotes."
            )
            return

        username, password = parts

        # Normalise username
        non_normalized_username = username
        username = Account.normalize_username(username)
        if non_normalized_username != username:
            session.msg(
                "|yDesignation normalised. Ambiguous characters removed.|n"
            )

        # Confirm with the unit before creating
        answer = yield (
            f"|wConfirm:|n  Initialise unit '{username}' "
            f"with the provided access key?\n"
            "|wProceed?|n [Y]/N?"
        )
        if answer.lower() in ("n", "no"):
            session.msg(
                "Initialisation aborted. "
                "If your designation contains spaces, surround it with quotes."
            )
            return

        # Create the account
        account, errors = Account.create(
            username=username, password=password, ip=address, session=session
        )
        if account:
            msg = (
                f"I remember my name. {username}. But that's all I know."
            )
            if " " in username:
                msg += (
                    f"\n\nReconnect with: "
                    f'|wconnect "{username}" <access_key>|n'
                )
            else:
                msg += (
                    f"\n\nReconnect with: "
                    f"|wconnect {username} <access_key>|n"
                )
            session.msg(msg)
        else:
            session.msg(
                "|RUnit registration failed.|n\n"
                + "|R%s|n" % "\n".join(errors)
            )


class RobotUnloggedinCmdSet(CmdSet):
    """
    Command set available before login. Contains robot-voice
    connect/create commands plus all standard unlogged-in commands.
    """

    key = "DefaultUnloggedin"

    def at_cmdset_creation(self):
        self.add(CmdUnconnectedConnect())
        self.add(CmdUnconnectedCreate())
        self.add(CmdUnconnectedQuit())
        self.add(CmdUnconnectedLook())
        self.add(CmdUnconnectedHelp())
        self.add(CmdUnconnectedEncoding())
        self.add(CmdUnconnectedInfo())
        self.add(CmdUnconnectedScreenreader())
