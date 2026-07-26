# Match — Queue Contracts

## Overview
- **Handler file:** `src/app/rabbit/api/match.py`
- **Service file:** `src/core/services/match.py`
- **Commands file:** `src/core/commands/match.py`
- **Results file:** `src/core/results/match.py`

## Queues Summary

| Queue | Command | Result | Description |
|-------|---------|--------|-------------|
| `event.match.setup` | `SetupMatchCommand` | `SingleMatchView` | Настройка одиночного матча |
| `event.match.result.record` | `RecordMatchResultCommand` | `SingleMatchView` | Запись результата матча |
| `event.match.get` | `GetMatchCommand` | `SingleMatchView` | Получение матча по ID |
| `event.match.list` | `ListMatchesCommand` | `list[SingleMatchView]` | Список матчей события |

---

## Queue: `event.match.setup`

### Command: `SetupMatchCommand`
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `access_data` | `AccessDataRequest` | Yes | |
| `event_id` | `UUID` | Yes | |
| `team_ids` | `list[UUID]` | Yes | Минимум 2 команды, без дубликатов |
| `draft_id` | `UUID \| None` | No | ID draft (если команды из draft) |
| `scheduled_at` | `datetime \| None` | No | Запланированное время |

### Result: `SingleMatchView`
→ См. [_shared/single-match-view.md](../../_shared/single-match-view.md#singlematchview)

**SingleMatchSlotView:** `slot_id` (UUID), `slot_num` (int), `team_id` (UUID), `score_id` (UUID), `score` (int)

### Exceptions
| Exception | Condition |
|-----------|-----------|
| `NotFoundException` | Событие/команда не найдено |
| `ForbiddenException` | Не организатор и нет `P_EVENT_ADMIN_MANAGE_BRACKET` или `P_EVENT_ADMIN_COMPLETE` |
| `BadRequestException` | match_type не SINGLE |
| `ConflictException` | Статус события не позволяет match setup |
| `BadRequestException` | Менее 2 команд / дубликаты |
| `BadRequestException` | Команда без игроков |
| `BadRequestException` | Команды из разных событий |
| `ConflictException` | Команды уже в активном матче |
| `ConflictException` | Draft уже в активном матче (если parallel drafts запрещены) |

---

## Queue: `event.match.result.record`

### Command: `RecordMatchResultCommand`
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `access_data` | `AccessDataRequest` | Yes | |
| `match_id` | `UUID` | Yes | |
| `scores` | `dict[UUID, int]` | Yes | team_id → score (неотрицательные) |

### Result: `SingleMatchView`
→ См. [_shared/single-match-view.md](../../_shared/single-match-view.md#singlematchview)

### Exceptions
| Exception | Condition |
|-----------|-----------|
| `NotFoundException` | Матч/событие/команда не найдено |
| `ForbiddenException` | Не организатор и нет `P_EVENT_ADMIN_MANAGE_BRACKET` |
| `BadRequestException` | Только single-game матчи |
| `BadRequestException` | Нет слотов / нет score row |
| `ConflictException` | Результат уже записан |
| `BadRequestException` | Negative scores / missing/extra scores |

---

## Queue: `event.match.get`

### Command: `GetMatchCommand`
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `match_id` | `UUID` | Yes | |
| `access_data` | `AccessDataRequest` | Yes | |

### Result: `SingleMatchView`
→ См. [_shared/single-match-view.md](../../_shared/single-match-view.md#singlematchview)

### Exceptions
| Exception | Condition |
|-----------|-----------|
| `NotFoundException` | Матч не найден |
| `ForbiddenException` | Нет доступа |

---

## Queue: `event.match.list`

### Command: `ListMatchesCommand`
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `event_id` | `UUID` | Yes | |
| `access_data` | `AccessDataRequest` | Yes | |
| `active` | `bool \| None` | No | Фильтр активных матчей |
| `pagination` | `PaginationRequest` | No | |

### Result: `list[SingleMatchView]`
→ См. [_shared/single-match-view.md](../../_shared/single-match-view.md#singlematchview)

### Exceptions
| Exception | Condition |
|-----------|-----------|
| `NotFoundException` | Событие не найдено |
| `ForbiddenException` | Нет доступа |
