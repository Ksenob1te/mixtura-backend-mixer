"""Restriction and permission helpers.
Mirrors Server Service src/infra/postgre/static/permissions.py and restrictions.py.
Bit positions follow canonical Server Service PERMISSION and RESTRICTION enum order.
"""

from enum import IntEnum
from uuid import UUID

from src.core.commands.access_data import AccessDataRequest


class PermissionCode(IntEnum):
    """Mirrors server PERMISSION enum order. Bit position = enum value."""
    ADMINISTRATOR = 0
    EDIT_NAME = 1
    EDIT_ROLES = 2
    CREATE_VIRTUAL = 3
    MIGRATE_MEMBERS = 4
    KICK_MEMBERS = 5
    CREATE_CUSTOM = 6
    DELETE_CUSTOM = 7
    EDIT_ALL_CUSTOMS = 8
    EDIT_SERVER_ROLES = 9
    EDIT_SERVER_PUBLIC = 10
    EDIT_SERVER_NAME = 11
    EDIT_SERVER_DESCRIPTION = 12
    EDIT_SERVER_BANNER = 13
    EDIT_SERVER_ICON = 14
    EDIT_SERVER_GAME = 15
    DELETE_SERVER = 16
    EDIT_ROLE_SET = 17
    EDIT_RATING_SET = 18
    EDIT_INVITES = 19
    RESTRICT_SERVER_BAN = 20
    RESTRICT_MIX_BAN = 21
    RESTRICT_TOURNAMENT_BAN = 22
    RESTRICT_SELF_EDIT_NAME = 23
    EVENT_CREATE = 24
    EVENT_ADMIN_VIEW = 25
    EVENT_ADMIN_UPDATE = 26
    EVENT_ADMIN_MANAGE_ORGANIZERS = 27
    EVENT_ADMIN_MANAGE_PLAYERS = 28
    EVENT_ADMIN_MANAGE_BRACKET = 29
    EVENT_ADMIN_CANCEL = 30
    EVENT_ADMIN_COMPLETE = 31


class RestrictionCode(IntEnum):
    """Mirrors server RESTRICTION enum order. Bit position = enum value."""
    SERVER_BAN = 0
    MIX_BAN = 1
    TOURNAMENT_BAN = 2
    SELF_EDIT_NAME = 3


# Pre-computed bit masks for event-relevant permissions
P_EVENT_CREATE = 1 << PermissionCode.EVENT_CREATE
P_EVENT_ADMIN_VIEW = 1 << PermissionCode.EVENT_ADMIN_VIEW
P_EVENT_ADMIN_UPDATE = 1 << PermissionCode.EVENT_ADMIN_UPDATE
P_EVENT_ADMIN_MANAGE_ORGANIZERS = 1 << PermissionCode.EVENT_ADMIN_MANAGE_ORGANIZERS
P_EVENT_ADMIN_MANAGE_PLAYERS = 1 << PermissionCode.EVENT_ADMIN_MANAGE_PLAYERS
P_EVENT_ADMIN_MANAGE_BRACKET = 1 << PermissionCode.EVENT_ADMIN_MANAGE_BRACKET
P_EVENT_ADMIN_CANCEL = 1 << PermissionCode.EVENT_ADMIN_CANCEL
P_EVENT_ADMIN_COMPLETE = 1 << PermissionCode.EVENT_ADMIN_COMPLETE

# Pre-computed bit masks for restrictions
R_SERVER_BAN = 1 << RestrictionCode.SERVER_BAN
R_MIX_BAN = 1 << RestrictionCode.MIX_BAN
R_TOURNAMENT_BAN = 1 << RestrictionCode.TOURNAMENT_BAN
R_SELF_EDIT_NAME = 1 << RestrictionCode.SELF_EDIT_NAME


def has_restriction(mask: int, bit: int) -> bool:
    return (mask & bit) != 0


def has_permission(mask: int, bit: int) -> bool:
    return (mask & bit) != 0


def is_same_server(access: AccessDataRequest, event_server_id: UUID) -> bool:
    return access.server_id == event_server_id


def has_event_admin_permission(access: AccessDataRequest, event_server_id: UUID, bit: int) -> bool:
    return is_same_server(access, event_server_id) and has_permission(access.permission_mask, bit)
