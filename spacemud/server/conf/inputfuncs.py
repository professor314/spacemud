"""
Input functions

Input functions are always called from the client (they handle server
input, hence the name).

This module is loaded by being included in the
`settings.INPUT_FUNC_MODULES` tuple.

All *global functions* included in this module are considered
input-handler functions and can be called by the client to handle
input.
"""


def text(session, *args, **kwargs):
    """
    Main text input handler. Called for every line of text input.
    Echoes the command back to the player before processing it.

    Args:
        session (Session): The active session.
        *args: Text input arguments.
        **kwargs: Additional keyword arguments.
    """
    # Get the raw text input
    text_input = args[0] if args else ""

    if text_input and text_input.strip():
        # Echo the command back to the player
        session.msg(f"|w> {text_input.strip()}|n")

    # Pass to Evennia's default text handler
    from evennia.server.inputfuncs import text as default_text
    default_text(session, *args, **kwargs)
