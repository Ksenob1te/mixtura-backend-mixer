# Team — Queue Contracts

## Overview
- **Handler file:** `src/infra/rabbit/api/team.py`
- **Service file:** `src/core/services/team.py`
- **Commands file:** `src/core/commands/team.py`

## Queues Summary

| Queue | Command | Result | Description |
|-------|---------|--------|-------------|
| `event.team.list` | `ListTeamsCommand` | `list[Team]` | Список команд события |

---

## Queue: `event.team.list`

### Command: `ListTeamsCommand`
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `event_id` | `UUID` | Yes | |
| `access_data` | `AccessDataRequest` | Yes | |
| `pagination` | `PaginationRequest` | No | |

### Result: `list[Team]`
Команда: id, event_id, draft_id, name, players (list[TeamPlayer]).

### Exceptions
| Exception | Condition |
|-----------|-----------|
| `NotFoundException` | Событие не найдено |
| `ForbiddenException` | Не организатор и нет `P_EVENT_ADMIN_MANAGE_BRACKET` |
