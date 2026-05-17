# Organizer — Queue Contracts

## Overview
- **Handler file:** `src/infra/rabbit/api/organizer.py`
- **Service file:** `src/core/services/organizer.py`
- **Commands file:** `src/core/commands/organizer.py`
- **Results file:** `src/core/results/organizer.py`

## Queues Summary

| Queue | Command | Result | Description |
|-------|---------|--------|-------------|
| `event.organizer.list` | `ListOrganizersCommand` | `list[OrganizerItem]` | Список организаторов события |
| `event.organizer.add` | `AddOrganizerCommand` | `OrganizerItem` | Добавление организатора |
| `event.organizer.remove` | `RemoveOrganizerCommand` | `StatusResponse` | Удаление организатора |

---

## Queue: `event.organizer.list`

### Command: `ListOrganizersCommand`
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `event_id` | `UUID` | Yes | |
| `access_data` | `AccessDataRequest` | Yes | |
| `pagination` | `PaginationRequest` | No | |

### Result: `list[OrganizerItem]`
| Field | Type | Description |
|-------|------|-------------|
| `id` | `UUID` | |
| `event_id` | `UUID` | |
| `member_id` | `UUID` | |

### Exceptions
| Exception | Condition |
|-----------|-----------|
| `NotFoundException` | Событие не найдено |
| `ForbiddenException` | Не организатор и нет `P_EVENT_ADMIN_VIEW`, событие не публичное |

---

## Queue: `event.organizer.add`

### Command: `AddOrganizerCommand`
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `access_data` | `AccessDataRequest` | Yes | |
| `event_id` | `UUID` | Yes | |
| `member_id` | `UUID` | Yes | ID добавляемого организатора |

### Result: `OrganizerItem`
Та же схема, что и в [`event.organizer.list`](#queue-eventorganizerlist).

### Exceptions
| Exception | Condition |
|-----------|-----------|
| `NotFoundException` | Событие не найдено |
| `ForbiddenException` | Не организатор и нет `P_EVENT_ADMIN_MANAGE_ORGANIZERS` |
| `BadRequestException` | Событие COMPLETED или CANCELLED |
| `ConflictException` | Member уже организатор |

---

## Queue: `event.organizer.remove`

### Command: `RemoveOrganizerCommand`
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `access_data` | `AccessDataRequest` | Yes | |
| `event_id` | `UUID` | Yes | |
| `member_id` | `UUID` | Yes | ID удаляемого организатора |

### Result: `StatusResponse`
→ См. [_shared/status-response.md](../../_shared/status-response.md)

### Exceptions
| Exception | Condition |
|-----------|-----------|
| `NotFoundException` | Событие не найдено / Member не организатор |
| `ForbiddenException` | Не организатор и нет `P_EVENT_ADMIN_MANAGE_ORGANIZERS` |
| `BadRequestException` | Событие COMPLETED или CANCELLED |
| `BadRequestException` | Нельзя удалить последнего организатора |
