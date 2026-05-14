# ApplicationService — Business Logic

## Overview
- **File:** `src/core/services/application.py`
- **Private helper:** `_can_view_event(access, event) -> bool` — проверка видимости события

## Dependencies

### Repositories
- `EventRepositoryProtocol` — загрузка события с relations
- `ApplicationRepositoryProtocol` — CRUD заявок, `get_by_event_and_member`, `list_by_event`
- `PlayerRepositoryProtocol` — CRUD EventPlayer, `get_by_event_and_member`
- `PlayerRoleRepositoryProtocol` — CRUD ролей игрока
- `FilledApplicationFieldRepositoryProtocol` — CRUD заполненных полей
- `ApplicationIntegrationRepositoryProtocol` — CRUD интеграций заявки

## Method: `submit(command: SubmitApplicationCommand) -> ApplicationSubmitResult`

### Purpose
Подача заявки на участие в событии. Создаёт Application, заполненные поля, интеграции, EventPlayer и PlayerRole.

### Algorithm
1. Загрузка event с time_settings, custom_fields, integrations, game_roles → `NotFoundException`
2. Проверка статуса: не COMPLETED/CANCELLED → `BadRequestException`
3. Проверка `member_id` не None → `ForbiddenException`
4. Проверка `server_id` совпадает → `ForbiddenException`
5. Проверка restriction: `R_MIX_BAN` для SINGLE, `R_TOURNAMENT_BAN` для TOURNAMENT → `ForbiddenException`
6. Проверка: нет существующей заявки → `ConflictException`
7. Проверка временного окна (time_settings) → `BadRequestException`
8. Валидация custom fields: нет дубликатов, все известны, все required предоставлены → `BadRequestException`
9. Валидация integrations: все required integration names предоставлены → `BadRequestException`
10. Валидация ролей: все известны, нет дубликатов → `BadRequestException`
11. Создание Application: если `use_application=False` → status=APPROVED, иначе PENDING
12. Создание FilledApplicationField для каждого filled_fields
13. Создание ApplicationIntegration для каждого integrations
14. Создание EventPlayer
15. Создание PlayerRole для каждой role_priority
16. Возврат `ApplicationSubmitResult`

### Exceptions
| Exception | Condition |
|-----------|-----------|
| `NotFoundException` | Событие не найдено |
| `BadRequestException` | Событие COMPLETED/CANCELLED |
| `ForbiddenException` | `member_id is None` |
| `ForbiddenException` | `server_id` не совпадает |
| `ForbiddenException` | `R_MIX_BAN` / `R_TOURNAMENT_BAN` |
| `ConflictException` | Заявка уже существует |
| `BadRequestException` | Время регистрации не наступило/истекло |
| `BadRequestException` | Дубликаты/unknown/missing custom fields |
| `BadRequestException` | Missing required integrations |
| `BadRequestException` | Unknown/duplicate game roles |

---

## Method: `review(command: ReviewApplicationCommand) -> ApplicationReviewResult`

### Purpose
Рассмотрение заявки организатором: approve, reject или waitlist.

### Algorithm
1. Загрузка application с filled_fields, integrations, event_player → `NotFoundException`
2. Загрузка event с organizers → `NotFoundException`
3. Проверка `is_same_server` → `ForbiddenException`
4. Проверка: организатор ИЛИ `P_EVENT_ADMIN_MANAGE_PLAYERS` → `ForbiddenException`
5. Проверка статуса события: не COMPLETED/CANCELLED → `BadRequestException`

**При APPROVED:**
6. Проверка `server_id` совпадает → `ForbiddenException`
7. Поиск существующего EventPlayer
8. Обновление application: is_approved=True, status=APPROVED
9. Если EventPlayer существует: проверка не PLAYING → `ConflictException`, обновление status=REGISTERED
10. Если EventPlayer не существует: создание нового
11. Если переданы role_priorities: валидация ролей, создание недостающих PlayerRole
12. Возврат `ApplicationReviewResult(player_id=...)`

**При REJECTED:**
6. Удаление EventPlayer (если есть)
7. Обновление application: is_approved=False, status=REJECTED
8. Возврат `ApplicationReviewResult(player_id=None)`

**При WAITLIST:**
6. Обновление application: is_approved=False, status=WAITLIST
7. Возврат `ApplicationReviewResult(player_id=None)`

### Exceptions
| Exception | Condition |
|-----------|-----------|
| `NotFoundException` | Заявка/событие не найдено |
| `ForbiddenException` | Не организатор и нет `P_EVENT_ADMIN_MANAGE_PLAYERS` |
| `BadRequestException` | Событие COMPLETED/CANCELLED |
| `ForbiddenException` | Approval с другого сервера |
| `ConflictException` | EventPlayer в статусе PLAYING |
| `BadRequestException` | Unsupported status |

---

## Method: `get(command: GetApplicationCommand) -> ApplicationDetail`

### Purpose
Получение детальной информации о заявке.

### Algorithm
1. Загрузка application с relations → `NotFoundException`
2. Загрузка event с organizers → `NotFoundException`
3. Проверка `is_same_server` → `ForbiddenException`
4. Проверка доступа: своя заявка ИЛИ `_can_view_event` ИЛИ `P_EVENT_ADMIN_MANAGE_PLAYERS` → `ForbiddenException`
5. Маппинг в `ApplicationDetail`

### Exceptions
| Exception | Condition |
|-----------|-----------|
| `NotFoundException` | Заявка/событие не найдено |
| `ForbiddenException` | Нет доступа |

---

## Method: `get_list(command: ListApplicationsCommand) -> list[ApplicationListItem]`

### Purpose
Получение списка заявок события с пагинацией и фильтрацией.

### Algorithm
1. Загрузка event с organizers → `NotFoundException`
2. Проверка `is_same_server` → `ForbiddenException`
3. Проверка доступа: `_can_view_event` ИЛИ `P_EVENT_ADMIN_MANAGE_PLAYERS` → `ForbiddenException`
4. Загрузка заявок через `application_repo.list_by_event` с pagination, status filter, sort
5. Маппинг в `ApplicationListItem`

### Exceptions
| Exception | Condition |
|-----------|-----------|
| `NotFoundException` | Событие не найдено |
| `ForbiddenException` | Нет доступа |
