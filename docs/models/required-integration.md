# RequiredIntegration

- **ORM file:** `src/core/models/required_integration.py`
- **Repo protocol:** `RequiredIntegrationRepositoryProtocol`
- **Used by services:** `SettingsService`, `ApplicationService`

## Role
Обязательная интеграция для события. Участники должны предоставить данные этой интеграции при подаче заявки.

## Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | `UUID` | Уникальный идентификатор |
| `name` | `str` | Название интеграции (уникально в рамках события, case-insensitive) |
| `event_id` | `UUID` | ID события |

## Relations

| Relation | Type | Description |
|----------|------|-------------|
| `event` | `Event \| None` | Родительское событие |

## Create/Update Models

### Create — `RequiredIntegrationCreate` (`src/core/models/required_integration.py`)

| Field | Type | Required | Default | Notes |
|-------|------|----------|---------|-------|
| `name` | `str` | Yes | — | |
| `event_id` | `UUID` | Yes | — | FK, неизменяем |

### Update — `RequiredIntegrationUpdate` (`src/core/models/required_integration.py`)

| Field | Type | Required | Default | Notes |
|-------|------|----------|---------|-------|
| `name` | `str \| None` | No | `None` | |

> Поле `event_id` неизменяемо и не включено в Update-модель.

### Read — `RequiredIntegration` (`src/core/models/required_integration.py`)

| Field | Type | Notes |
|-------|------|-------|
| `id` | `UUID` | |
| `name` | `str` | |
| `event_id` | `UUID` | |
| `event` | `Event \| None` | Навигационное свойство |
