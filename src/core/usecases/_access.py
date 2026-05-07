"""Restriction and permission bitmask positions.
Must match Server Service bit assignments.
"""

R_SERVER_BAN = 1 << 0
R_MIX_BAN = 1 << 1
R_TOURNAMENT_BAN = 1 << 2

P_EVENT_CREATE = 1 << 5
P_EVENT_ADMIN_VIEW = 1 << 6
P_EVENT_ADMIN_UPDATE = 1 << 7
P_EVENT_ADMIN_MANAGE_ORGANIZERS = 1 << 8
P_EVENT_ADMIN_MANAGE_PLAYERS = 1 << 9
P_EVENT_ADMIN_MANAGE_BRACKET = 1 << 10
P_EVENT_ADMIN_CANCEL = 1 << 11
P_EVENT_ADMIN_COMPLETE = 1 << 12


def has_restriction(mask: int, bit: int) -> bool:
    return (mask & bit) != 0


def has_permission(mask: int, bit: int) -> bool:
    return (mask & bit) != 0
