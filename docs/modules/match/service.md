# MatchService — Business Logic

## Overview
- **File:** `src/core/services/match.py`
- **Private helper:** `_build_single_match_view(match, event_id, bracket_id, stage_id, group_id, team_repo) -> SingleMatchView`

## Dependencies

### Repositories
- `EventRepositoryProtocol` — загрузка события
- `BracketRepositoryProtocol` — CRUD Bracket, `list_by_event`
- `StageRepositoryProtocol` — CRUD Stage, `list_by_bracket`
- `StageGroupRepositoryProtocol` — CRUD StageGroup, `list_by_stage`
- `MatchRepositoryProtocol` — CRUD Match, `get_event_context`, `list_by_event`, `count_incomplete_matches_by_event`, `list_active_team_ids_by_event`, `list_active_draft_ids_by_event`, `next_match_index`
- `MatchSlotRepositoryProtocol` — CRUD MatchSlot
- `MatchScoreRepositoryProtocol` — CRUD MatchScore
- `TeamRepositoryProtocol` — CRUD Team, загрузка с players
- `DraftRepositoryProtocol` — загрузка Draft
- `PlayerRepositoryProtocol` — CRUD EventPlayer, `get_by_event_and_member`

### Clients
- `RatingClient` — `process_match_result()` (RabbitMQ)

### Config
- `env.rating_match_process_enabled` — флаг публикации рейтингов

## Method: `setup(cmd: SetupMatchCommand) -> SingleMatchView`

### Purpose
Настройка одиночного матча: создание bracket/stage/group (если нет), match, slots, scores.

### Algorithm
1. Загрузка event с organizers → `NotFoundException`
2. Проверка `is_same_server` → `ForbiddenException`
3. Проверка: организатор ИЛИ `P_EVENT_ADMIN_MANAGE_BRACKET` ИЛИ `P_EVENT_ADMIN_COMPLETE` → `ForbiddenException`
4. Проверка match_type == SINGLE → `BadRequestException`
5. Проверка статуса: не CREATED/COMPLETED/CANCELLED → `ConflictException`
6. Проверка team_ids: >= 2, без дубликатов → `BadRequestException`
7. Загрузка команд: проверка event_id совпадает, есть игроки → `NotFoundException` / `BadRequestException`
8. Разрешение draft_id: из command или из команд → проверка consistency
9. Проверка "не заняты": команды не в активном матче, draft не в активном матче → `ConflictException`
10. **Get or create bracket:** `bracket_repo.list_by_event(event_id, 0, 1)` → если нет, создать
11. **Get or create stage:** поиск SINGLE_MATCH stage → если нет и есть другие stages → `ConflictException`, иначе создать
12. **Get or create group:** `stage_group_repo.list_by_stage(stage_id)` → если нет, создать
13. Создание Match с match_index = `next_match_index(group_id)`
14. Для каждой команды: создание MatchSlot (MANUAL) + MatchScore (score=0)
15. Возврат `SingleMatchView`

### Exceptions
| Exception | Condition |
|-----------|-----------|
| `NotFoundException` | Событие/команда не найдено |
| `ForbiddenException` | `server_id` не совпадает |
| `ForbiddenException` | Не организатор и нет `P_EVENT_ADMIN_MANAGE_BRACKET`/`P_EVENT_ADMIN_COMPLETE` |
| `BadRequestException` | match_type не SINGLE |
| `ConflictException` | Статус CREATED/COMPLETED/CANCELLED |
| `BadRequestException` | < 2 команды / дубликаты |
| `BadRequestException` | Команда без игроков / из другого события |
| `ConflictException` | Команды/драфт уже в активном матче |

---

## Method: `record_result(cmd: RecordMatchResultCommand) -> RecordedMatchResult`

### Purpose
Запись результата матча: валидация scores, определение победителя, обновление рейтингов, запись snapshot.

### Algorithm
1. `match_repo.get_event_context(match_id)` → event_id, server_id, stage_format, bracket_id, stage_id, group_id → `NotFoundException`
2. Загрузка event с organizers → `NotFoundException`
3. Проверка server_id consistency → `ForbiddenException`
4. Проверка: организатор ИЛИ `P_EVENT_ADMIN_MANAGE_BRACKET` → `ForbiddenException`
5. Проверка: match_type == SINGLE и stage_format == SINGLE_MATCH → `BadRequestException`
6. Загрузка match с slots → `NotFoundException`
7. Проверка: time_end is None (не завершён) → `ConflictException`
8. Проверка: есть слоты → `BadRequestException`
9. **Валидация scores:** все слоты имеют score row, scores для всех команд, нет неизвестных, нет отрицательных → `BadRequestException`
10. Проверка forfeit_team_ids: все известны, не все команды → `BadRequestException`
11. **Определение результата:**
    - Forfeit: winner = не-forfeit команда (если одна), ranks: forfeit=2.0, остальные=1.0
    - winner_id: ranks: winner=1.0, остальные=2.0
    - is_draw: все ranks=1.0
    - По scores: max score = winner, если несколько = draw
12. **Build rating payload:** сбор данных команд и игроков
13. Обновление MatchScore для каждого слота
14. Обновление EventPlayer.status = REGISTERED для всех игроков команд
15. Если `env.rating_match_process_enabled`: вызов `rating_client.process_match_result()` → rating_published=True
16. Создание result_snapshot
17. Обновление Match: time_start, time_end=now, result_snapshot
18. Построение `SingleMatchView` → возврат `RecordedMatchResult`

### Exceptions
| Exception | Condition |
|-----------|-----------|
| `NotFoundException` | Матч/событие/команда не найдено |
| `ForbiddenException` | `server_id` не совпадает |
| `ForbiddenException` | Не организатор и нет `P_EVENT_ADMIN_MANAGE_BRACKET` |
| `BadRequestException` | Только single-game матчи |
| `BadRequestException` | Нет слотов / нет score row |
| `ConflictException` | Результат уже записан |
| `BadRequestException` | Negative scores / missing/extra scores |
| `BadRequestException` | Unknown forfeit teams |
| `BadRequestException` | Forfeit + winner_id/draw |
| `BadRequestException` | Все команды forfeit |
| `BadRequestException` | winner_id + draw |

---

## Method: `get(cmd: GetMatchCommand) -> SingleMatchView`

### Purpose
Получение матча по ID.

### Algorithm
1. `match_repo.get_event_context(match_id)` → `NotFoundException`
2. Загрузка event с organizers → `NotFoundException`
3. Проверка server_id → `NotFoundException` если не совпадает
4. Проверка `is_same_server` → `ForbiddenException`
5. Проверка доступа: организатор ИЛИ `P_EVENT_ADMIN_VIEW` ИЛИ `P_EVENT_ADMIN_MANAGE_BRACKET` → если событие не публичное → `ForbiddenException`
6. Загрузка match с slots → `NotFoundException`
7. `_build_single_match_view()` → возврат

---

## Method: `get_list(cmd: ListMatchesCommand) -> list[SingleMatchView]`

### Purpose
Получение списка матчей события с пагинацией.

### Algorithm
1. Загрузка event с organizers → `NotFoundException`
2. Проверка `is_same_server` → `ForbiddenException`
3. Проверка доступа: организатор ИЛИ `P_EVENT_ADMIN_VIEW` ИЛИ `P_EVENT_ADMIN_MANAGE_BRACKET` → если не публичное → `ForbiddenException`
4. `match_repo.list_by_event(event_id, offset, limit, active=cmd.active)`
5. Для каждого матча: `get_event_context` → `_build_single_match_view()`
6. Возврат списка
