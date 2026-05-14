# SettingsService — Business Logic

## Overview
- **File:** `src/core/services/settings.py`
- **Private helper:** `_to_detail(event) -> EventDetail` — маппинг в EventDetail (дублирует helper из EventService)

## Dependencies

### Repositories
- `EventRepositoryProtocol` — загрузка события с relations
- `RequiredIntegrationRepositoryProtocol` — CRUD интеграций, `list_by_event`
- `SelectedGameRoleRepositoryProtocol` — CRUD ролей, `list_by_event`
- `ApplicationCustomFieldRepositoryProtocol` — CRUD полей, `list_by_event`
- `ApplicationTimeSettingsRepositoryProtocol` — CRUD time settings, `get_by_event_id`

## Common Pattern
Все методы изменения настроек следуют единому паттерну:
1. Загрузка event с organizers → `NotFoundException`
2. Проверка `is_same_server` → `ForbiddenException`
3. Проверка: организатор ИЛИ `P_EVENT_ADMIN_UPDATE` → `ForbiddenException`
4. Проверка статуса: CREATED или IDLE → `BadRequestException`
5. Операция (create/update/delete)
6. Загрузка полной модели → возврат `_to_detail(event)`

---

## Method: `add_integration(command: AddIntegrationCommand) -> EventDetail`

### Purpose
Добавление обязательной интеграции для события.

### Algorithm
1-4. Common pattern
5. Проверка: нет интеграции с таким name (case-insensitive) → `ConflictException`
6. `integration_repo.create(RequiredIntegrationCreate(name, event_id))`
7. Загрузка полной модели → возврат

---

## Method: `remove_integration(command: RemoveIntegrationCommand) -> EventDetail`

### Purpose
Удаление обязательной интеграции.

### Algorithm
1-4. Common pattern
5. Проверка: integration существует и принадлежит событию → `NotFoundException`
6. `integration_repo.delete(integration_id)`
7. Загрузка полной модели → возврат

---

## Method: `add_game_role(command: AddGameRoleCommand) -> EventDetail`

### Purpose
Добавление игровой роли в событие.

### Algorithm
1-4. Common pattern
5. Проверка: game_role_id ещё не добавлена → `ConflictException`
6. `role_repo.create(SelectedGameRoleCreate(game_role_id, event_id, override_max_count, override_min_count))`
7. Загрузка полной модели → возврат

---

## Method: `update_game_role(command: UpdateGameRoleCommand) -> EventDetail`

### Purpose
Обновление override-лимитов игровой роли.

### Algorithm
1-4. Common pattern
5. Проверка: role существует и принадлежит событию → `NotFoundException`
6. `role_repo.update(SelectedGameRoleUpdate(id, override_max_count, override_min_count))`
7. Загрузка полной модели → возврат

---

## Method: `remove_game_role(command: RemoveGameRoleCommand) -> EventDetail`

### Purpose
Удаление игровой роли из события.

### Algorithm
1-4. Common pattern
5. Проверка: role существует и принадлежит событию → `NotFoundException`
6. `role_repo.delete(selected_role_id)`
7. Загрузка полной модели → возврат

---

## Method: `add_custom_field(command: AddCustomFieldCommand) -> EventDetail`

### Purpose
Добавление кастомного поля формы заявки.

### Algorithm
1-4. Common pattern
5. Проверка: `event.use_application=True` → `BadRequestException`
6. Проверка: нет поля с таким name (case-insensitive) → `ConflictException`
7. `field_repo.create(ApplicationCustomFieldCreate(event_id, name, is_private, is_required))`
8. Загрузка полной модели → возврат

---

## Method: `update_custom_field(command: UpdateCustomFieldCommand) -> EventDetail`

### Purpose
Обновление кастомного поля.

### Algorithm
1-4. Common pattern
5. Проверка: `event.use_application=True` → `BadRequestException`
6. Проверка: field существует и принадлежит событию → `NotFoundException`
7. `field_repo.update(ApplicationCustomFieldUpdate(id, name, is_private, is_required))`
8. Загрузка полной модели → возврат

---

## Method: `remove_custom_field(command: RemoveCustomFieldCommand) -> EventDetail`

### Purpose
Удаление кастомного поля.

### Algorithm
1-4. Common pattern
5. Проверка: `event.use_application=True` → `BadRequestException`
6. Проверка: field существует и принадлежит событию → `NotFoundException`
7. `field_repo.delete(field_id)`
8. Загрузка полной модели → возврат

---

## Method: `update_time_settings(command: UpdateTimeSettingsCommand) -> EventDetail`

### Purpose
Обновление временных окон регистрации.

### Algorithm
1-4. Common pattern
5. Проверка: `event.use_application=True` → `BadRequestException`
6. Проверка: start_time < end_time (если оба заданы) → `BadRequestException`
7. Конвертация времени в UTC без tzinfo
8. Если time_settings существует → update, иначе → create
9. Загрузка полной модели → возврат

---

## Method: `get_application_form_settings(command: GetApplicationFormSettingsCommand) -> ApplicationFormSettingsResponse`

### Purpose
Получение настроек формы заявки для отображения участникам.

### Algorithm
1. Загрузка event с organizers → `NotFoundException`
2. Проверка: `event.use_application=True` → `BadRequestException`
3. Проверка `is_same_server` → `ForbiddenException`
4. Проверка доступа:
   - Организатор/admin — всегда
   - Иначе: статус == REGISTRATION → иначе `BadRequestException` ("Registration not open yet" или "Registration is closed")
5. Загрузка integrations, roles, fields, time_settings
6. Фильтрация custom_fields: если member_id задан — все, иначе — только не-private
7. Возврат `ApplicationFormSettingsResponse`

### Exceptions
| Exception | Condition |
|-----------|-----------|
| `NotFoundException` | Событие не найдено |
| `BadRequestException` | use_application=False |
| `ForbiddenException` | `server_id` не совпадает |
| `BadRequestException` | Регистрация не открыта (не REGISTRATION статус) |
