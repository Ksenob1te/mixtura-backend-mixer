# ApplicationTimeSettings

- **ORM file:** `src/core/models/application_time_settings.py`
- **Repo protocol:** `ApplicationTimeSettingsRepositoryProtocol`
- **Used by services:** `EventService`, `SettingsService`, `ApplicationService`

## Role
Временные окна для приёма заявок. Если заданы, заявки принимаются только в указанный период.

## Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | `UUID` | Уникальный идентификатор |
| `event_id` | `UUID` | ID события |
| `start_time` | `datetime \| None` | Начало приёма заявок, при None — ручное начало |
| `end_time` | `datetime \| None` | Конец приёма заявок, при None — ручное окончание |

## Relations

| Relation | Type | Description |
|----------|------|-------------|
| `event` | `Event \| None` | Родительское событие |

## Create/Update Models

### Create — `ApplicationTimeSettingsCreate` (`src/core/models/application_time_settings.py`)

| Field | Type | Required | Default | Notes |
|-------|------|----------|---------|-------|
| `event_id` | `UUID` | Yes | — | FK, неизменяем |
| `start_time` | `datetime \| None` | No | `None` | |
| `end_time` | `datetime \| None` | No | `None` | |

### Update — `ApplicationTimeSettingsUpdate` (`src/core/models/application_time_settings.py`)

| Field | Type | Required | Default | Notes |
|-------|------|----------|---------|-------|
| `start_time` | `datetime \| None` | No | `None` | |
| `end_time` | `datetime \| None` | No | `None` | |

> Поле `event_id` неизменяемо и не включено в Update-модель.

### Read — `ApplicationTimeSettings` (`src/core/models/application_time_settings.py`)

| Field | Type | Notes |
|-------|------|-------|
| `id` | `UUID` | |
| `event_id` | `UUID` | |
| `start_time` | `datetime \| None` | |
| `end_time` | `datetime \| None` | |
| `event` | `Event \| None` | Навигационное свойство |
