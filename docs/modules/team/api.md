# Team — Queue Contracts

## Overview
- **Handler file:** `src/app/rabbit/api/team.py`
- **Service file:** `src/core/services/team.py`
- **Commands file:** `src/core/commands/team.py`
- **Results file:** `src/core/results/team.py`

## Queues Summary

| Queue | Command | Result | Description |
|-------|---------|--------|-------------|
| `event.team.list` | `ListTeamsCommand` | `list[TeamItem]` | Список команд события |

---

## Queue: `event.team.list`

### Command: `ListTeamsCommand`
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `event_id` | `UUID` | Yes | |
| `access_data` | `AccessDataRequest` | Yes | |
| `pagination` | `PaginationRequest` | No | |

### Result: `list[TeamItem]`
| Field | Type | Description |
|-------|------|-------------|
| `id` | `UUID` | |
| `event_id` | `UUID` | |
| `draft_id` | `UUID \| None` | |
| `name` | `str` | |

### Exceptions
| Exception | Condition |
|-----------|-----------|
| `NotFoundException` | Событие не найдено |
| `ForbiddenException` | Не организатор и нет `P_EVENT_ADMIN_MANAGE_BRACKET` |
