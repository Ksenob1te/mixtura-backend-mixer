# EventService — Business Logic

## Overview
- **File:** `src/core/services/event.py`
- **Private helper:** `_to_detail(event) -> EventDetail` — маппинг ORM-модели в EventDetail

## Dependencies

### Repositories
- `EventRepositoryProtocol` — CRUD событий, `transition_status`, `list_by_server`
- `OrganizerRepositoryProtocol` — CRUD организаторов, `list_by_event`
- `ApplicationTimeSettingsRepositoryProtocol` — CRUD временных настроек
- `MatchRepositoryProtocol` — `count_incomplete_matches_by_event`

## Method: `create(command: CreateEventCommand) -> EventDetail`

### Purpose
Создание нового события с автоматическим назначением создателя как организатора.

### Algorithm
1. Проверка `access_data.member_id` не None → `ForbiddenException`
2. Проверка permission `P_EVENT_CREATE` → `ForbiddenException`
3. Создание Event через `event_repo.create(EventCreate(...))`
4. Создание Organizer через `organizer_repo.create(OrganizerCreate(event_id, member_id))`
5. Если `use_application=True` → создание ApplicationTimeSettings
6. Загрузка полной модели со всеми relations → возврат `_to_detail(event)`

### Exceptions
| Exception | Condition |
|-----------|-----------|
| `ForbiddenException` | `member_id is None` |
| `ForbiddenException` | Нет `P_EVENT_CREATE` |

---

## Method: `get(command: GetEventCommand) -> EventDetail`

### Purpose
Получение полной карточки события по ID.

### Algorithm
1. Загрузка event со всеми relations → `NotFoundException` если нет
2. Проверка `is_same_server(access, event.server_id)` → `ForbiddenException`
3. Возврат `_to_detail(event)`

### Exceptions
| Exception | Condition |
|-----------|-----------|
| `NotFoundException` | Событие не найдено |
| `ForbiddenException` | `server_id` не совпадает |

---

## Method: `get_list(command: ListEventsCommand) -> list[EventCard]`

### Purpose
Получение списка событий сервера, видимых конкретному пользователю, с пагинацией.

### Algorithm
1. Проверка `is_same_server(access, server_id)` → `ForbiddenException`
2. Проверка `access.member_id is not None` → `ForbiddenException`
3. Вызов `event_repo.list_visible_to_member(server_id, member_id, offset, limit)` — один SQL-запрос:
   - `is_public=True` ИЛИ пользователь организатор ИЛИ пользователь участник (EventPlayer)
   - `ORDER BY name`, `OFFSET/LIMIT` из пагинации
4. Маппинг в `EventCard`

### Exceptions
| Exception | Condition |
|-----------|-----------|
| `ForbiddenException` | `server_id` не совпадает |
| `ForbiddenException` | `member_id is None` |

---

## Method: `update(command: UpdateEventCommand) -> EventDetail`

### Purpose
Обновление настроек события.

### Algorithm
1. Загрузка event с organizers → `NotFoundException`
2. Проверка `is_same_server` → `ForbiddenException`
3. Проверка: организатор ИЛИ `P_EVENT_ADMIN_UPDATE` → `ForbiddenException`
4. Проверка статуса: только CREATED или IDLE → `BadRequestException`
5. Создание `EventUpdate` из command (exclude access_data, event_id, unset fields)
6. `event_repo.update(event_id, update)`
7. Загрузка полной модели → возврат `_to_detail`

### Exceptions
| Exception | Condition |
|-----------|-----------|
| `NotFoundException` | Событие не найдено |
| `ForbiddenException` | `server_id` не совпадает |
| `ForbiddenException` | Не организатор и нет `P_EVENT_ADMIN_UPDATE` |
| `BadRequestException` | Статус не CREATED или IDLE |

---

## Method: `activate(command: ActivateEventCommand) -> EventDetail`

### Purpose
Перевод события из CREATED в IDLE (готово к работе).

### Algorithm
1. Загрузка event с organizers → `NotFoundException`
2. Проверка `is_same_server` → `ForbiddenException`
3. Проверка: организатор ИЛИ `P_EVENT_ADMIN_UPDATE` → `ForbiddenException`
4. `event_repo.transition_status(event_id, EventStatus.IDLE)`
5. Загрузка полной модели → возврат `_to_detail`

### Exceptions
| Exception | Condition |
|-----------|-----------|
| `NotFoundException` | Событие не найдено |
| `ForbiddenException` | `server_id` не совпадает |
| `ForbiddenException` | Не организатор и нет `P_EVENT_ADMIN_UPDATE` |

---

## Method: `open_registration(command: OpenRegistrationCommand) -> EventDetail`

### Purpose
Открытие регистрации: статус → REGISTRATION.

### Algorithm
1. Загрузка event с organizers → `NotFoundException`
2. Проверка `is_same_server` → `ForbiddenException`
3. Проверка: организатор ИЛИ `P_EVENT_ADMIN_UPDATE` → `ForbiddenException`
4. `event_repo.transition_status(event_id, EventStatus.REGISTRATION)`
5. Загрузка полной модели → возврат `_to_detail`

### Exceptions
| Exception | Condition |
|-----------|-----------|
| `NotFoundException` | Событие не найдено |
| `ForbiddenException` | `server_id` не совпадает |
| `ForbiddenException` | Не организатор и нет `P_EVENT_ADMIN_UPDATE` |

---

## Method: `close_registration(command: CloseRegistrationCommand) -> EventDetail`

### Purpose
Закрытие регистрации: статус → IDLE.

### Algorithm
1. Загрузка event с organizers → `NotFoundException`
2. Проверка `is_same_server` → `ForbiddenException`
3. Проверка: организатор ИЛИ `P_EVENT_ADMIN_UPDATE` → `ForbiddenException`
4. `event_repo.transition_status(event_id, EventStatus.IDLE)`
5. Загрузка полной модели → возврат `_to_detail`

### Exceptions
| Exception | Condition |
|-----------|-----------|
| `NotFoundException` | Событие не найдено |
| `ForbiddenException` | `server_id` не совпадает |
| `ForbiddenException` | Не организатор и нет `P_EVENT_ADMIN_UPDATE` |

---

## Method: `cancel(command: CancelEventCommand) -> EventDetail`

### Purpose
Отмена события: статус → CANCELLED.

### Algorithm
1. Загрузка event с organizers → `NotFoundException`
2. Проверка `is_same_server` → `ForbiddenException`
3. Проверка: организатор ИЛИ `P_EVENT_ADMIN_CANCEL` → `ForbiddenException`
4. `event_repo.transition_status(event_id, EventStatus.CANCELLED)`
5. Загрузка полной модели → возврат `_to_detail`

### Exceptions
| Exception | Condition |
|-----------|-----------|
| `NotFoundException` | Событие не найдено |
| `ForbiddenException` | `server_id` не совпадает |
| `ForbiddenException` | Не организатор и нет `P_EVENT_ADMIN_CANCEL` |

---

## Method: `complete(command: CompleteEventCommand) -> EventDetail`

### Purpose
Завершение single-game события: статус → COMPLETED.

### Algorithm
1. Загрузка event с organizers → `NotFoundException`
2. Проверка `is_same_server` → `ForbiddenException`
3. Проверка: организатор ИЛИ `P_EVENT_ADMIN_COMPLETE` → `ForbiddenException`
4. Проверка `match_type == SINGLE` → `BadRequestException`
5. Проверка статуса не COMPLETED/CANCELLED → `ConflictException`
6. Проверка `match_repo.count_incomplete_matches_by_event(event_id) == 0` → `ConflictException` если > 0
7. `event_repo.transition_status(event_id, EventStatus.COMPLETED)`
8. Загрузка полной модели → возврат `_to_detail`

### Exceptions
| Exception | Condition |
|-----------|-----------|
| `NotFoundException` | Событие не найдено |
| `ForbiddenException` | `server_id` не совпадает |
| `ForbiddenException` | Не организатор и нет `P_EVENT_ADMIN_COMPLETE` |
| `BadRequestException` | `match_type` не SINGLE |
| `ConflictException` | Статус COMPLETED или CANCELLED |
| `ConflictException` | Есть активные матчи |
