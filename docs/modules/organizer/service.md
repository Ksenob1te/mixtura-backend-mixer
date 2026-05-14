# OrganizerService — Business Logic

## Overview
- **File:** `src/core/services/organizer.py`

## Dependencies

### Repositories
- `OrganizerRepositoryProtocol` — CRUD организаторов, `list_by_event`
- `EventRepositoryProtocol` — загрузка события с organizers

## Method: `get_list(command: ListOrganizersCommand) -> list[OrganizerItem]`

### Purpose
Получение списка всех организаторов события.

### Algorithm
1. Загрузка event с organizers → `NotFoundException`
2. Проверка `is_same_server` → `ForbiddenException`
3. Проверка доступа: организатор ИЛИ `P_EVENT_ADMIN_VIEW` → если нет и событие не публичное → `ForbiddenException`
4. `organizer_repo.list_by_event(event_id)` → маппинг в `OrganizerItem`

### Exceptions
| Exception | Condition |
|-----------|-----------|
| `NotFoundException` | Событие не найдено |
| `ForbiddenException` | `server_id` не совпадает |
| `ForbiddenException` | Не организатор и нет `P_EVENT_ADMIN_VIEW`, событие не публичное |

---

## Method: `add(command: AddOrganizerCommand) -> OrganizerItem`

### Purpose
Добавление нового организатора в событие.

### Algorithm
1. Загрузка event с organizers → `NotFoundException`
2. Проверка `is_same_server` → `ForbiddenException`
3. Проверка: организатор ИЛИ `P_EVENT_ADMIN_MANAGE_ORGANIZERS` → `ForbiddenException`
4. Проверка статуса: не COMPLETED/CANCELLED → `BadRequestException`
5. Проверка: member ещё не организатор → `ConflictException`
6. `organizer_repo.create(OrganizerCreate(event_id, member_id))` → возврат `OrganizerItem`

### Exceptions
| Exception | Condition |
|-----------|-----------|
| `NotFoundException` | Событие не найдено |
| `ForbiddenException` | `server_id` не совпадает |
| `ForbiddenException` | Не организатор и нет `P_EVENT_ADMIN_MANAGE_ORGANIZERS` |
| `BadRequestException` | Событие COMPLETED/CANCELLED |
| `ConflictException` | Member уже организатор |

---

## Method: `remove(command: RemoveOrganizerCommand) -> None`

### Purpose
Удаление организатора из события.

### Algorithm
1. Загрузка event с organizers → `NotFoundException`
2. Проверка `is_same_server` → `ForbiddenException`
3. Проверка: организатор ИЛИ `P_EVENT_ADMIN_MANAGE_ORGANIZERS` → `ForbiddenException`
4. Проверка статуса: не COMPLETED/CANCELLED → `BadRequestException`
5. Проверка: организаторов > 1 → `BadRequestException` (нельзя удалить последнего)
6. Поиск target по member_id → `NotFoundException` если нет
7. `organizer_repo.delete(target.id)`

### Exceptions
| Exception | Condition |
|-----------|-----------|
| `NotFoundException` | Событие не найдено / Member не организатор |
| `ForbiddenException` | `server_id` не совпадает |
| `ForbiddenException` | Не организатор и нет `P_EVENT_ADMIN_MANAGE_ORGANIZERS` |
| `BadRequestException` | Событие COMPLETED/CANCELLED |
| `BadRequestException` | Последний организатор |
