# DraftService — Business Logic

## Overview
- **File:** `src/core/services/draft.py`
- **Private helper:** `_resolve_busy_players(event_id, allow_multiple) -> set[UUID]` — нахождение игроков, занятых в активных матчах

## Dependencies

### Repositories
- `EventRepositoryProtocol` — загрузка события
- `OrganizerRepositoryProtocol` — не используется напрямую (проверка через event.organizers)
- `PlayerRepositoryProtocol` — CRUD EventPlayer, `list_by_event`
- `DraftRepositoryProtocol` — CRUD Draft, `list_by_event`
- `DraftedPlayerRepositoryProtocol` — CRUD DraftedPlayer
- `MatchRepositoryProtocol` — `list_active_draft_ids_by_event`

## Method: `create(cmd: CreateDraftCommand) -> Draft`

### Purpose
Создание draft-сессии: выбор доступных игроков, создание Draft и DraftedPlayer записей, обновление статуса игроков на SELECTED.

### Algorithm
1. Загрузка event с organizers → `NotFoundException`
2. Проверка `is_same_server` → `ForbiddenException`
3. Проверка: организатор ИЛИ `P_EVENT_ADMIN_MANAGE_PLAYERS` → `ForbiddenException`
4. Проверка статуса: REGISTRATION, IDLE или IN_PROGRESS → `BadRequestException`
5. Определение пула игроков:
   - Если `player_ids` заданы: проверка каждого (event_id совпадает, статус допустим) → `NotFoundException` / `BadRequestException`
   - Иначе: `player_repo.list_by_event` для каждого статуса из `statuses` (default: REGISTERED, BENCHED)
   - Если `pinned_only`: фильтр по `is_draft_pinned`
6. Разрешение занятых игроков: если `allow_multiple_drafts=False` → поиск игроков в активных матчах через `match_repo.list_active_draft_ids_by_event`
7. Фильтрация доступных (не занятых)
8. Применение `limit` если задан
9. Проверка: есть доступные → `ConflictException` если нет
10. Создание Draft
11. Для каждого доступного игрока: создание DraftedPlayer + обновление статуса на SELECTED
12. Загрузка draft с drafted_players → возврат

### Допустимые статусы игроков
- Без `allow_multiple_drafts`: REGISTERED, BENCHED
- С `allow_multiple_drafts`: REGISTERED, BENCHED, SELECTED

### Exceptions
| Exception | Condition |
|-----------|-----------|
| `NotFoundException` | Событие/игрок не найден |
| `ForbiddenException` | `server_id` не совпадает |
| `ForbiddenException` | Не организатор и нет `P_EVENT_ADMIN_MANAGE_PLAYERS` |
| `BadRequestException` | Статус события не позволяет draft |
| `BadRequestException` | Игрок не в допустимом статусе |
| `ConflictException` | Нет доступных игроков |

---

## Method: `get(cmd: GetDraftCommand) -> Draft`

### Purpose
Получение draft-сессии по ID с drafted_players.

### Algorithm
1. Загрузка draft с drafted_players → `NotFoundException`
2. Загрузка event с organizers → `NotFoundException`
3. Проверка `is_same_server` → `ForbiddenException`
4. Проверка: организатор ИЛИ `P_EVENT_ADMIN_MANAGE_PLAYERS` → `ForbiddenException`
5. Возврат draft

---

## Method: `get_list(cmd: ListDraftsCommand) -> list[Draft]`

### Purpose
Получение списка draft-сессий события с пагинацией.

### Algorithm
1. Загрузка event с organizers → `NotFoundException`
2. Проверка `is_same_server` → `ForbiddenException`
3. Проверка: организатор ИЛИ `P_EVENT_ADMIN_MANAGE_PLAYERS` → `ForbiddenException`
4. `draft_repo.list_by_event(event_id, offset, limit)` → возврат
