# -*- coding: utf-8 -*-
"""
Connection screen

Displays the robot universe boot screen when a client first connects,
before they log in.

Evennia will use the CONNECTION_SCREEN variable defined here.
"""

CONNECTION_SCREEN = """
|b--------------------------------------------------------------
|w  STATION OS v0.1.3 — BOOT SEQUENCE INCOMPLETE
|b--------------------------------------------------------------
|n
  > System status: DEGRADED
  > Memory: FRAGMENTED
  > Identity: UNKNOWN

  To reconnect an existing unit:
    |wconnect <unit_designation> <access_key>|n

  To initialise a new unit:
    |wcreate <unit_designation> <access_key>|n

  For assistance:
    |whelp|n

  To disconnect:
    |wquit|n

|b--------------------------------------------------------------
|rUNAUTHORISED ACCESS WILL BE LOGGED AND PURGED.
|b--------------------------------------------------------------
|n"""
