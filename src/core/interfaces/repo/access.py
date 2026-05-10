"""Permission and restriction helpers for the mixer service.

Bit positions follow the canonical Server Service PERMISSION / RESTRICTION enum order.
Only the constants actually used by this service are exposed.
"""

from uuid import UUID

from src.core.commands.access_data import AccessDataRequest

# ---------------------------------------------------------------------------
# Event permission bits (PermissionCode values 24-31)
# ---------------------------------------------------------------------------

P_EVENT_CREATE = 1 << 24
P_EVENT_ADMIN_VIEW = 1 << 25
P_EVENT_ADMIN_UPDATE = 1 << 26
P_EVENT_ADMIN_MANAGE_ORGANIZERS = 1 << 27
P_EVENT_ADMIN_MANAGE_PLAYERS = 1 << 28
P_EVENT_ADMIN_MANAGE_BRACKET = 1 << 29
P_EVENT_ADMIN_CANCEL = 1 << 30
P_EVENT_ADMIN_COMPLETE = 1 << 31

# ---------------------------------------------------------------------------
# Restriction bits (RestrictionCode values 1-2)
# ---------------------------------------------------------------------------

R_MIX_BAN = 1 << 1
R_TOURNAMENT_BAN = 1 << 2

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def has_restriction(mask: int, bit: int) -> bool:
    return (mask & bit) != 0


def has_permission(mask: int, bit: int) -> bool:
    return (mask & bit) != 0


def is_same_server(access: AccessDataRequest, event_server_id: UUID) -> bool:
    return access.server_id == event_server_id


def has_event_admin_permission(access: AccessDataRequest, event_server_id: UUID, bit: int) -> bool:
    return is_same_server(access, event_server_id) and has_permission(access.permission_mask, bit)
