# PlayerService — Business Logic

## Overview
- **File:** `src/core/services/player.py`

## Dependencies

### Repositories
- `EventRepositoryProtocol` — загрузка события с organizers
- `PlayerRepositoryProtocol` — CRUD EventPlayer, `list_by_event`, `get_by_event_and_member`

## Method: `get_list(command: ListPlayersCommand) -> list[PlayerItem]`

### Purpose
Получение списка участников события с пагинацией и фильтрацией по статусу.

### Algorithm
1. Загрузка event с organizers → `NotFoundException`
2. Проверка `is_same_server` → `ForbiddenException`
3. Проверка: организатор ИЛИ `P_EVENT_ADMIN_MANAGE_PLAYERS` → `ForbiddenException`
4. `player_repo.list_by_event(event_id, offset, limit, status)` → преобразование в `PlayerItem`

### Exceptions
| Exception | Condition |
|-----------|-----------|
| `NotFoundException` | Событие не найдено |
| `ForbiddenException` | `server_id` не совпадает |
| `ForbiddenException` | Не организатор и нет `P_EVENT_ADMIN_MANAGE_PLAYERS` |

---

## Method: `update_status(command: UpdatePlayerStatusCommand) -> PlayerUpdateResult`

### Purpose
Обновление статуса участника события.

### Algorithm
1. Загрузка event с organizers → `NotFoundException`
2. Проверка `is_same_server` → `ForbiddenException`
3. Проверка: организатор ИЛИ `P_EVENT_ADMIN_MANAGE_PLAYERS` → `ForbiddenException`
4. Проверка статуса события: не CANCELLED → `BadRequestException`
5. Поиск player по event_id + member_id → `NotFoundException`
6. Если player.status == PLAYING и новый статус != PLAYING → `BadRequestException`
7. `player_repo.update(player.id, EventPlayerUpdate(status=command.status, custom_id=command.custom_id))` → возврат `PlayerUpdateResult`

### Exceptions
| Exception | Condition |
|-----------|-----------|
| `NotFoundException` | Событие/участник не найден |
| `ForbiddenException` | `server_id` не совпадает |
| `ForbiddenException` | Не организатор и нет `P_EVENT_ADMIN_MANAGE_PLAYERS` |
| `BadRequestException` | Событие CANCELLED |
| `BadRequestException` | Нельзя изменить статус PLAYING игрока |

---

## Method: `remove(command: RemovePlayerCommand) -> None`

### Purpose
Удаление участника из события.

### Algorithm
1. Загрузка event с organizers → `NotFoundException`
2. Проверка `is_same_server` → `ForbiddenException`
3. Проверка: организатор ИЛИ `P_EVENT_ADMIN_MANAGE_PLAYERS` → `ForbiddenException`
4. Проверка статуса события: не CANCELLED → `BadRequestException`
5. Поиск player по event_id + member_id → `NotFoundException`
6. Если player.status == PLAYING → `BadRequestException`
7. `player_repo.delete(player.id)`

### Exceptions
| Exception | Condition |
|-----------|-----------|
| `NotFoundException` | Событие/участник не найден |
| `ForbiddenException` | `server_id` не совпадает |
| `ForbiddenException` | Не организатор и нет `P_EVENT_ADMIN_MANAGE_PLAYERS` |
| `BadRequestException` | Событие CANCELLED |
| `BadRequestException` | Нельзя удалить PLAYING игрока |
