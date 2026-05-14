# RequiredIntegration

- **ORM file:** `src/core/models/required_integration.py`
- **Repo protocol:** `RequiredIntegrationRepositoryProtocol`
- **Used by services:** `SettingsService`, `ApplicationService`

## Role
Обязательная интеграция для события. Many-to-many связь между событием и внешним провайдером интеграции. Участники должны предоставить данные этой интеграции при подаче заявки.

## Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | `UUID` | Уникальный идентификатор |
| `provider_id` | `UUID` | ID внешнего провайдера интеграции (неизменяем) |
| `event_id` | `UUID` | ID события |

## Relations

| Relation | Type | Description |
|----------|------|-------------|
| `event` | `Event \| None` | Родительское событие |

## Create/Update Models

### Create — `RequiredIntegrationCreate` (`src/core/models/required_integration.py`)

| Field | Type | Required | Default | Notes |
|-------|------|----------|---------|-------|
| `provider_id` | `UUID` | Yes | — | FK, неизменяем |
| `event_id` | `UUID` | Yes | — | FK, неизменяем |

### Update

Update-модель отсутствует. Записи не обновляются.

> Поля `id`, `provider_id` и `event_id` неизменяемы и не включены в Update-модель.

### Read — `RequiredIntegration` (`src/core/models/required_integration.py`)

| Field | Type | Notes |
|-------|------|-------|
| `id` | `UUID` | |
| `provider_id` | `UUID` | |
| `event_id` | `UUID` | |
| `event` | `Event \| None` | Навигационное свойство |
