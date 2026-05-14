# TeamService — Business Logic

## Overview
- **File:** `src/core/services/team.py`

## Dependencies

### Repositories
- `TeamRepositoryProtocol` — `list_by_event`
- `EventRepositoryProtocol` — загрузка события

## Method: `get_list(cmd: ListTeamsCommand) -> list[Team]`

### Purpose
Получение списка команд события с пагинацией.

### Algorithm
1. Загрузка event с organizers → `NotFoundException`
2. Проверка `is_same_server` → `ForbiddenException`
3. Проверка: организатор ИЛИ `P_EVENT_ADMIN_MANAGE_BRACKET` → `ForbiddenException`
4. `team_repo.list_by_event(event_id, offset, limit)` → возврат

### Exceptions
| Exception | Condition |
|-----------|-----------|
| `NotFoundException` | Событие не найдено |
| `ForbiddenException` | `server_id` не совпадает |
| `ForbiddenException` | Не организатор и нет `P_EVENT_ADMIN_MANAGE_BRACKET` |
