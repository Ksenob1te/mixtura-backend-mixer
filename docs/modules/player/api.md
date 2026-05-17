# Player — Queue Contracts

## Overview
- **Handler file:** `src/infra/rabbit/api/player.py`
- **Service file:** `src/core/services/player.py`
- **Commands file:** `src/core/commands/player.py`
- **Results file:** `src/core/results/player.py`

## Queues Summary

| Queue | Command | Result | Description |
|-------|---------|--------|-------------|
| `event.player.list` | `ListPlayersCommand` | `list[PlayerItem]` | Список участников события |
| `event.player.status.update` | `UpdatePlayerStatusCommand` | `PlayerUpdateResult` | Обновление статуса участника |
| `event.player.remove` | `RemovePlayerCommand` | `StatusResponse` | Удаление участника |

---

## Queue: `event.player.list`

### Command: `ListPlayersCommand`
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `event_id` | `UUID` | Yes | |
| `access_data` | `AccessDataRequest` | Yes | |
| `status` | `EventPlayerStatus \| None` | No | Фильтр по статусу |
| `pagination` | `PaginationRequest` | No | |

### Result: `list[PlayerItem]`
| Field | Type | Description |
|-------|------|-------------|
| `id` | `UUID` | |
| `member_id` | `UUID` | |
| `status` | `EventPlayerStatus` | |
| `is_draft_pinned` | `bool` | |
| `application_id` | `UUID \| None` | |
| `custom_id` | `UUID \| None` | ID оценки игрока (рейтинг) |

### Exceptions
| Exception | Condition |
|-----------|-----------|
| `NotFoundException` | Событие не найдено |
| `ForbiddenException` | Не организатор и нет `P_EVENT_ADMIN_MANAGE_PLAYERS` |

---

## Queue: `event.player.status.update`

### Command: `UpdatePlayerStatusCommand`
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `access_data` | `AccessDataRequest` | Yes | |
| `event_id` | `UUID` | Yes | |
| `member_id` | `UUID` | Yes | ID участника |
| `status` | `EventPlayerStatus` | Yes | Новый статус |
| `custom_id` | `UUID \| None` | No | ID оценки игрока (рейтинг) |

### Result: `PlayerUpdateResult`
| Field | Type | Description |
|-------|------|-------------|
| `id` | `UUID` | |
| `member_id` | `UUID` | |
| `status` | `EventPlayerStatus` | |
| `custom_id` | `UUID \| None` | |

### Exceptions
| Exception | Condition |
|-----------|-----------|
| `NotFoundException` | Событие/участник не найден |
| `ForbiddenException` | Не организатор и нет `P_EVENT_ADMIN_MANAGE_PLAYERS` |
| `BadRequestException` | Событие CANCELLED |
| `BadRequestException` | Нельзя изменить статус PLAYING игрока |

---

## Queue: `event.player.remove`

### Command: `RemovePlayerCommand`
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `access_data` | `AccessDataRequest` | Yes | |
| `event_id` | `UUID` | Yes | |
| `member_id` | `UUID` | Yes | ID участника |

### Result: `StatusResponse`
→ См. [_shared/status-response.md](../../_shared/status-response.md)

### Exceptions
| Exception | Condition |
|-----------|-----------|
| `NotFoundException` | Событие/участник не найден |
| `ForbiddenException` | Не организатор и нет `P_EVENT_ADMIN_MANAGE_PLAYERS` |
| `BadRequestException` | Событие CANCELLED |
| `BadRequestException` | Нельзя удалить PLAYING игрока |
