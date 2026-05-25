# PlayerService — Business Logic

## Overview
- **File:** `src/core/services/player.py`

## Dependencies

### Repositories
- `EventRepositoryProtocol` — загрузка события с organizers
- `PlayerRepositoryProtocol` — CRUD EventPlayer, `list_by_event`, `get_by_event_and_member`, `list_by_ids`
- `PlayerRoleRepositoryProtocol` — CRUD PlayerRole, `list_by_player`

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

## Method: `get_bulk(command: GetBulkPlayersCommand) -> list[PlayerItem]`

### Purpose
Массовое получение участников события по списку ID. Возвращает только участников, принадлежащих указанному событию.

### Algorithm
1. Загрузка event с organizers → `NotFoundException`
2. Проверка `is_same_server` → `ForbiddenException`
3. Проверка: организатор ИЛИ `P_EVENT_ADMIN_MANAGE_PLAYERS` → `ForbiddenException`
4. `player_repo.list_by_ids(event_id, player_ids)` → преобразование в `list[PlayerItem]`

### Exceptions
| Exception | Condition |
|-----------|-----------|
| `NotFoundException` | Событие не найдено |
| `ForbiddenException` | `server_id` не совпадает |
| `ForbiddenException` | Не организатор и нет `P_EVENT_ADMIN_MANAGE_PLAYERS` |

---

## Method: `add(command: AddPlayerCommand) -> PlayerAddResult`

### Purpose
Добавление игрока организатором напрямую, без заявки (в первую очередь для виртуальных игроков).

### Algorithm
1. Загрузка event с organizers → `NotFoundException`
2. Проверка `is_same_server` → `ForbiddenException`
3. Проверка: организатор ИЛИ `P_EVENT_ADMIN_MANAGE_PLAYERS` → `ForbiddenException`
4. Проверка статуса события: не COMPLETED/CANCELLED → `BadRequestException`
5. Проверка на дубликат (`get_by_event_and_member`) → `ConflictException`
6. `player_repo.create(EventPlayerCreate(...))` → `PlayerAddResult`

### Exceptions
| Exception | Condition |
|-----------|-----------|
| `NotFoundException` | Событие не найдено |
| `ForbiddenException` | `server_id` не совпадает |
| `ForbiddenException` | Не организатор и нет `P_EVENT_ADMIN_MANAGE_PLAYERS` |
| `BadRequestException` | Событие COMPLETED или CANCELLED |
| `ConflictException` | Игрок уже в событии |

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

## Method: `update_roles(command: UpdatePlayerRolesCommand) -> PlayerRolesUpdateResult`

### Purpose
Полная замена ролей и их приоритетов для игрока. Роли из списка создаются/обновляются, отсутствующие — удаляются.

### Algorithm
1. Загрузка event с organizers + game_roles → `NotFoundException`
2. Проверка `is_same_server` → `ForbiddenException`
3. Проверка: организатор ИЛИ `P_EVENT_ADMIN_MANAGE_PLAYERS` → `ForbiddenException`
4. Проверка статуса события: не COMPLETED/CANCELLED → `BadRequestException`
5. Поиск player по event_id + member_id → `NotFoundException`
6. Построение `role_id_map` (как в ApplicationService: `selected_game_role.id` и `game_role_id`)
7. Валидация: неизвестные роли → `BadRequestException`, дубликаты → `BadRequestException`
8. Загрузка существующих ролей игрока
9. Удаление ролей, не вошедших в новый список
10. Для каждой роли из команды: update (если существует) или create (если новая)
11. Возврат `PlayerRolesUpdateResult` с актуальным списком ролей

### Exceptions
| Exception | Condition |
|-----------|-----------|
| `NotFoundException` | Событие/участник не найден |
| `ForbiddenException` | `server_id` не совпадает |
| `ForbiddenException` | Не организатор и нет `P_EVENT_ADMIN_MANAGE_PLAYERS` |
| `BadRequestException` | Событие COMPLETED или CANCELLED |
| `BadRequestException` | Неизвестная роль или дубликат |

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
