# Settings — Queue Contracts

## Overview
- **Handler file:** `src/infra/rabbit/api/settings.py`
- **Service file:** `src/core/services/settings.py`
- **Commands file:** `src/core/commands/settings.py`
- **Results file:** `src/core/results/event.py` (EventDetail, ApplicationFormSettingsResponse)

## Queues Summary

| Queue | Command | Result | Description |
|-------|---------|--------|-------------|
| `event.settings.integration.add` | `AddIntegrationCommand` | `EventDetail` | Добавление обязательной интеграции |
| `event.settings.integration.remove` | `RemoveIntegrationCommand` | `EventDetail` | Удаление обязательной интеграции |
| `event.settings.roles.add` | `AddGameRoleCommand` | `EventDetail` | Добавление игровой роли |
| `event.settings.roles.update` | `UpdateGameRoleCommand` | `EventDetail` | Обновление игровой роли |
| `event.settings.roles.remove` | `RemoveGameRoleCommand` | `EventDetail` | Удаление игровой роли |
| `event.settings.custom_fields.add` | `AddCustomFieldCommand` | `EventDetail` | Добавление кастомного поля |
| `event.settings.custom_fields.update` | `UpdateCustomFieldCommand` | `EventDetail` | Обновление кастомного поля |
| `event.settings.custom_fields.remove` | `RemoveCustomFieldCommand` | `EventDetail` | Удаление кастомного поля |
| `event.settings.time_settings.update` | `UpdateTimeSettingsCommand` | `EventDetail` | Обновление временных настроек |
| `event.application.form_settings` | `GetApplicationFormSettingsCommand` | `ApplicationFormSettingsResponse` | Получение настроек формы заявки |

---

## Integration Queues

### `event.settings.integration.add`
**Command:** `AddIntegrationCommand` — `access_data`, `event_id`, `name` (str)
**Result:** `EventDetail` → См. [_shared/event-detail.md](../../_shared/event-detail.md#eventdetail)
**Exceptions:** `NotFoundException`, `ForbiddenException` (не организатор/`P_EVENT_ADMIN_UPDATE`), `BadRequestException` (статус не CREATED/IDLE), `ConflictException` (дубликат имени)

### `event.settings.integration.remove`
**Command:** `RemoveIntegrationCommand` — `access_data`, `event_id`, `integration_id`
**Result:** `EventDetail` → См. [_shared/event-detail.md](../../_shared/event-detail.md#eventdetail)
**Exceptions:** `NotFoundException`, `ForbiddenException`, `BadRequestException` (статус не CREATED/IDLE)

---

## Game Role Queues

### `event.settings.roles.add`
**Command:** `AddGameRoleCommand` — `access_data`, `event_id`, `game_role_id`, `override_max_count` (int|None), `override_min_count` (int|None)
**Result:** `EventDetail` → См. [_shared/event-detail.md](../../_shared/event-detail.md#eventdetail)
**Exceptions:** `NotFoundException`, `ForbiddenException`, `BadRequestException` (статус не CREATED/IDLE), `ConflictException` (роль уже добавлена)

### `event.settings.roles.update`
**Command:** `UpdateGameRoleCommand` — `access_data`, `event_id`, `selected_role_id`, `override_max_count` (int|None), `override_min_count` (int|None)
**Result:** `EventDetail` → См. [_shared/event-detail.md](../../_shared/event-detail.md#eventdetail)
**Exceptions:** `NotFoundException`, `ForbiddenException`, `BadRequestException` (статус не CREATED/IDLE)

### `event.settings.roles.remove`
**Command:** `RemoveGameRoleCommand` — `access_data`, `event_id`, `selected_role_id`
**Result:** `EventDetail` → См. [_shared/event-detail.md](../../_shared/event-detail.md#eventdetail)
**Exceptions:** `NotFoundException`, `ForbiddenException`, `BadRequestException` (статус не CREATED/IDLE)

---

## Custom Field Queues

### `event.settings.custom_fields.add`
**Command:** `AddCustomFieldCommand` — `access_data`, `event_id`, `name`, `is_private` (bool, default False), `is_required` (bool, default False)
**Result:** `EventDetail` → См. [_shared/event-detail.md](../../_shared/event-detail.md#eventdetail)
**Exceptions:** `NotFoundException`, `ForbiddenException`, `BadRequestException` (статус не CREATED/IDLE или use_application=False), `ConflictException` (дубликат имени)

### `event.settings.custom_fields.update`
**Command:** `UpdateCustomFieldCommand` — `access_data`, `event_id`, `field_id`, `name` (str|None), `is_private` (bool|None), `is_required` (bool|None)
**Result:** `EventDetail` → См. [_shared/event-detail.md](../../_shared/event-detail.md#eventdetail)
**Exceptions:** `NotFoundException`, `ForbiddenException`, `BadRequestException` (статус не CREATED/IDLE или use_application=False)

### `event.settings.custom_fields.remove`
**Command:** `RemoveCustomFieldCommand` — `access_data`, `event_id`, `field_id`
**Result:** `EventDetail` → См. [_shared/event-detail.md](../../_shared/event-detail.md#eventdetail)
**Exceptions:** `NotFoundException`, `ForbiddenException`, `BadRequestException` (статус не CREATED/IDLE или use_application=False)

---

## Time Settings Queue

### `event.settings.time_settings.update`
**Command:** `UpdateTimeSettingsCommand` — `access_data`, `event_id`, `start_time` (datetime|None), `end_time` (datetime|None)
**Result:** `EventDetail` → См. [_shared/event-detail.md](../../_shared/event-detail.md#eventdetail)
**Exceptions:** `NotFoundException`, `ForbiddenException`, `BadRequestException` (статус не CREATED/IDLE, use_application=False, start_time >= end_time)

---

## Application Form Settings Queue

### `event.application.form_settings`
**Command:** `GetApplicationFormSettingsCommand` — `event_id`, `access_data`

**Result:** `ApplicationFormSettingsResponse`
| Field | Type | Description |
|-------|------|-------------|
| `event_id` | `UUID` | |
| `event_name` | `str` | |
| `required_integrations` | `list[RequiredIntegrationResponse]` | |
| `available_roles` | `list[SelectedGameRoleResponse]` | |
| `custom_fields` | `list[ApplicationCustomFieldResponse]` | Private поля скрыты для не-авторизованных |
| `time_settings` | `ApplicationTimeSettingsResponse \| None` | |

**Access Rules:**
- Организатор/admin — всегда доступно
- Иначе: статус должен быть REGISTRATION → иначе `BadRequestException`

**Exceptions:** `NotFoundException`, `ForbiddenException`, `BadRequestException` (use_application=False, регистрация не открыта)
