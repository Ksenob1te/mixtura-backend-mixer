# Draft — Queue Contracts

## Overview
- **Handler file:** `src/infra/rabbit/api/draft.py`
- **Service file:** `src/core/services/draft.py`
- **Commands file:** `src/core/commands/draft.py`

## Queues Summary

| Queue | Command | Result | Description |
|-------|---------|--------|-------------|
| `event.draft.create` | `CreateDraftCommand` | `Draft` | Создание draft-сессии |
| `event.draft.get` | `GetDraftCommand` | `Draft` | Получение draft по ID |
| `event.draft.list` | `ListDraftsCommand` | `list[Draft]` | Список draft-сессий события |

---

## Queue: `event.draft.create`

### Command: `CreateDraftCommand`
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `access_data` | `AccessDataRequest` | Yes | |
| `event_id` | `UUID` | Yes | |
| `player_ids` | `list[UUID] \| None` | No | Конкретные игроки для draft |
| `statuses` | `list[EventPlayerStatus] \| None` | No | Фильтр по статусам (default: REGISTERED, BENCHED) |
| `limit` | `int \| None` | No | Макс. количество игроков |
| `pinned_only` | `bool` | No | Только закреплённые игроки |

### Result: `Draft`
Draft с загруженными drafted_players.

### Exceptions
| Exception | Condition |
|-----------|-----------|
| `NotFoundException` | Событие/игрок не найден |
| `ForbiddenException` | Не организатор и нет `P_EVENT_ADMIN_MANAGE_PLAYERS` |
| `BadRequestException` | Статус события не позволяет draft |
| `BadRequestException` | Игрок не в допустимом статусе |
| `ConflictException` | Нет доступных игроков |

---

## Queue: `event.draft.get`

### Command: `GetDraftCommand`
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `draft_id` | `UUID` | Yes | |
| `access_data` | `AccessDataRequest` | Yes | |

### Exceptions
| Exception | Condition |
|-----------|-----------|
| `NotFoundException` | Draft не найден |
| `ForbiddenException` | Нет доступа |

---

## Queue: `event.draft.list`

### Command: `ListDraftsCommand`
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `event_id` | `UUID` | Yes | |
| `access_data` | `AccessDataRequest` | Yes | |
| `pagination` | `PaginationRequest` | No | |

### Exceptions
| Exception | Condition |
|-----------|-----------|
| `NotFoundException` | Событие не найдено |
| `ForbiddenException` | Нет доступа |
