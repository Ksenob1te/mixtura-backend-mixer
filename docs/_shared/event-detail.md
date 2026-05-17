# EventDetail

- **Source:** `src/core/results/event.py`
- **Used by queues:** все очереди `event.*` (create, get, list, update, activate, registration.open/close, cancel, complete), все очереди `event.settings.*` (integration.add/remove, roles.add/update/remove, custom_fields.add/update/remove, time_settings.update)

## EventDetail

| Field | Type | Description |
|-------|------|-------------|
| `id` | `UUID` | ID события |
| `name` | `str` | Название события |
| `match_type` | `EventMatchType` | SINGLE или TOURNAMENT |
| `use_application` | `bool` | Требуется ли заявка |
| `is_public` | `bool` | Публичное ли событие |
| `team_size` | `int` | Размер команды |
| `team_formation` | `TeamFormation` | DRAFT, BALANCE или MANUAL |
| `status` | `EventStatus` | Текущий статус |
| `allow_multiple_drafts` | `bool` | Разрешены ли параллельные draft-сессии |
| `rating_set_id` | `UUID \| None` | Набор рейтингов |
| `server_id` | `UUID` | ID сервера |
| `organizers` | `list[OrganizerResponse]` | Организаторы события |
| `required_integrations` | `list[RequiredIntegrationResponse]` | Обязательные интеграции |
| `selected_game_roles` | `list[SelectedGameRoleResponse]` | Игровые роли |
| `time_settings` | `ApplicationTimeSettingsResponse \| None` | Временные настройки регистрации |
| `custom_fields` | `list[ApplicationCustomFieldResponse]` | Кастомные поля заявки |

## EventCard

- **Source:** `src/core/results/event.py`
- **Used by:** `event.list`

| Field | Type | Description |
|-------|------|-------------|
| `id` | `UUID` | ID события |
| `name` | `str` | Название события |
| `match_type` | `EventMatchType` | SINGLE или TOURNAMENT |
| `use_application` | `bool` | Требуется ли заявка |
| `is_public` | `bool` | Публичное ли событие |
| `team_size` | `int` | Размер команды |
| `team_formation` | `TeamFormation` | DRAFT, BALANCE или MANUAL |
| `status` | `EventStatus` | Текущий статус |
| `server_id` | `UUID` | ID сервера |

## Nested Types

### OrganizerResponse

| Field | Type | Description |
|-------|------|-------------|
| `id` | `UUID` | |
| `member_id` | `UUID` | |

### RequiredIntegrationResponse

| Field | Type | Description |
|-------|------|-------------|
| `id` | `UUID` | |
| `provider_id` | `UUID` | |

### SelectedGameRoleResponse

| Field | Type | Description |
|-------|------|-------------|
| `id` | `UUID` | |
| `game_role_id` | `UUID` | |
| `override_max_count` | `int \| None` | Переопределённый максимум игроков на роль |
| `override_min_count` | `int \| None` | Переопределённый минимум игроков на роль |

### ApplicationTimeSettingsResponse

| Field | Type | Description |
|-------|------|-------------|
| `id` | `UUID` | |
| `start_time` | `datetime \| None` | Начало окна регистрации |
| `end_time` | `datetime \| None` | Конец окна регистрации |

### ApplicationCustomFieldResponse

| Field | Type | Description |
|-------|------|-------------|
| `id` | `UUID` | |
| `name` | `str` | Название поля |
| `is_private` | `bool` | Скрытое ли поле |
| `is_required` | `bool` | Обязательное ли поле |
