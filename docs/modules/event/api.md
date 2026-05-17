# Event — Queue Contracts

## Overview
- **Handler file:** `src/infra/rabbit/api/event.py`
- **Service file:** `src/core/services/event.py`
- **Commands file:** `src/core/commands/event.py`
- **Results file:** `src/core/results/event.py`

## Queues Summary

| Queue | Command | Result | Description |
|-------|---------|--------|-------------|
| `event.create` | `CreateEventCommand` | `EventDetail` | Создание нового события |
| `event.get` | `GetEventCommand` | `EventDetail` | Получение события по ID |
| `event.list` | `ListEventsCommand` | `list[EventCard]` | Список событий сервера |
| `event.update` | `UpdateEventCommand` | `EventDetail` | Обновление настроек события |
| `event.activate` | `ActivateEventCommand` | `EventDetail` | Активация (CREATED → IDLE) |
| `event.registration.open` | `OpenRegistrationCommand` | `EventDetail` | Открытие регистрации (→ REGISTRATION) |
| `event.registration.close` | `CloseRegistrationCommand` | `EventDetail` | Закрытие регистрации (→ IDLE) |
| `event.cancel` | `CancelEventCommand` | `EventDetail` | Отмена события (→ CANCELLED) |
| `event.complete` | `CompleteEventCommand` | `EventDetail` | Завершение события (→ COMPLETED) |

---

## Queue: `event.create`

### Command: `CreateEventCommand`
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `access_data` | `AccessDataRequest` | Yes | Авторизация. Требуется `member_id` и бит `P_EVENT_CREATE` |
| `name` | `str` | Yes | Название события |
| `match_type` | `EventMatchType` | Yes | SINGLE или TOURNAMENT |
| `use_application` | `bool` | Yes | Требуется ли заявка |
| `is_public` | `bool` | Yes | Публичное ли событие |
| `team_size` | `int` | Yes | Размер команды |
| `team_formation` | `TeamFormation` | Yes | DRAFT, BALANCE или MANUAL |
| `allow_multiple_drafts` | `bool` | Yes | Параллельные draft-сессии |
| `rating_set_id` | `UUID \| None` | No | Набор рейтингов |

### Result: `EventDetail`
→ См. [_shared/event-detail.md](../../_shared/event-detail.md#eventdetail)

### Behavior
- Создаёт Event, добавляет создателя как Organizer
- Если `use_application=True` — создаёт пустые ApplicationTimeSettings
- Возвращает `ResponseMessage[EventDetail]` со статусом 200

### Exceptions
| Exception | Condition |
|-----------|-----------|
| `ForbiddenException` | `member_id is None` |
| `ForbiddenException` | Нет `P_EVENT_CREATE` |

---

## Queue: `event.get`

### Command: `GetEventCommand`
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `event_id` | `UUID` | Yes | ID события |
| `access_data` | `AccessDataRequest` | Yes | Авторизация |

### Result: `EventDetail`
→ См. [_shared/event-detail.md](../../_shared/event-detail.md#eventdetail)

### Exceptions
| Exception | Condition |
|-----------|-----------|
| `NotFoundException` | Событие не найдено |
| `ForbiddenException` | `server_id` не совпадает |

---

## Queue: `event.list`

### Command: `ListEventsCommand`
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `server_id` | `UUID` | Yes | ID сервера |
| `access_data` | `AccessDataRequest` | Yes | Авторизация |

### Result: `list[EventCard]`
→ См. [_shared/event-detail.md](../../_shared/event-detail.md#eventcard)

### Behavior
- Фильтрация: публичные события видны всем, непубличные — только организаторам и admin с `P_EVENT_ADMIN_VIEW`
- Возвращает до 100 событий

### Exceptions
| Exception | Condition |
|-----------|-----------|
| `ForbiddenException` | `server_id` не совпадает |

---

## Queue: `event.update`

### Command: `UpdateEventCommand`
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `access_data` | `AccessDataRequest` | Yes | Авторизация |
| `event_id` | `UUID` | Yes | ID события |
| `name` | `str \| None` | No | Новое название |
| `match_type` | `EventMatchType \| None` | No | Новый тип матча |
| `use_application` | `bool \| None` | No | |
| `is_public` | `bool \| None` | No | |
| `team_size` | `int \| None` | No | |
| `team_formation` | `TeamFormation \| None` | No | |
| `allow_multiple_drafts` | `bool \| None` | No | |
| `rating_set_id` | `UUID \| None` | No | |

### Result: `EventDetail`
→ См. [_shared/event-detail.md](../../_shared/event-detail.md#eventdetail)

### Exceptions
| Exception | Condition |
|-----------|-----------|
| `NotFoundException` | Событие не найдено |
| `ForbiddenException` | `server_id` не совпадает |
| `ForbiddenException` | Не организатор и нет `P_EVENT_ADMIN_UPDATE` |
| `BadRequestException` | Статус не CREATED или IDLE |

---

## Queue: `event.activate`

### Command: `ActivateEventCommand`
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `access_data` | `AccessDataRequest` | Yes | |
| `event_id` | `UUID` | Yes | |

### Result: `EventDetail`
Переход статуса → IDLE. → См. [_shared/event-detail.md](../../_shared/event-detail.md#eventdetail)

### Exceptions
| Exception | Condition |
|-----------|-----------|
| `NotFoundException` | Событие не найдено |
| `ForbiddenException` | Не организатор и нет `P_EVENT_ADMIN_UPDATE` |

---

## Queue: `event.registration.open`

### Command: `OpenRegistrationCommand`
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `access_data` | `AccessDataRequest` | Yes | |
| `event_id` | `UUID` | Yes | |

### Result: `EventDetail`
Переход статуса → REGISTRATION. → См. [_shared/event-detail.md](../../_shared/event-detail.md#eventdetail)

### Exceptions
| Exception | Condition |
|-----------|-----------|
| `NotFoundException` | Событие не найдено |
| `ForbiddenException` | Не организатор и нет `P_EVENT_ADMIN_UPDATE` |

---

## Queue: `event.registration.close`

### Command: `CloseRegistrationCommand`
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `access_data` | `AccessDataRequest` | Yes | |
| `event_id` | `UUID` | Yes | |

### Result: `EventDetail`
Переход статуса → IDLE. → См. [_shared/event-detail.md](../../_shared/event-detail.md#eventdetail)

### Exceptions
| Exception | Condition |
|-----------|-----------|
| `NotFoundException` | Событие не найдено |
| `ForbiddenException` | Не организатор и нет `P_EVENT_ADMIN_UPDATE` |

---

## Queue: `event.cancel`

### Command: `CancelEventCommand`
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `access_data` | `AccessDataRequest` | Yes | |
| `event_id` | `UUID` | Yes | |

### Result: `EventDetail`
Переход статуса → CANCELLED. → См. [_shared/event-detail.md](../../_shared/event-detail.md#eventdetail)

### Exceptions
| Exception | Condition |
|-----------|-----------|
| `NotFoundException` | Событие не найдено |
| `ForbiddenException` | Не организатор и нет `P_EVENT_ADMIN_CANCEL` |

---

## Queue: `event.complete`

### Command: `CompleteEventCommand`
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `access_data` | `AccessDataRequest` | Yes | |
| `event_id` | `UUID` | Yes | |

### Result: `EventDetail`
Переход статуса → COMPLETED. → См. [_shared/event-detail.md](../../_shared/event-detail.md#eventdetail)

### Exceptions
| Exception | Condition |
|-----------|-----------|
| `NotFoundException` | Событие не найдено |
| `ForbiddenException` | Не организатор и нет `P_EVENT_ADMIN_COMPLETE` |
| `BadRequestException` | `match_type` не SINGLE |
| `ConflictException` | Статус COMPLETED или CANCELLED |
| `ConflictException` | Есть активные матчи |
