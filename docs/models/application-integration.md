# ApplicationIntegration

- **ORM file:** `src/core/models/application_integration.py`
- **Repo protocol:** `ApplicationIntegrationRepositoryProtocol`
- **Used by services:** `ApplicationService`

## Role
Интеграция, привязанная к заявке. Связывает участника с внешним провайдером (Steam, Discord и т.д.).
Провайдер является внешней сущностью относительно данного сервиса.

## Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | `UUID` | Уникальный идентификатор |
| `application_id` | `UUID` | ID заявки |
| `user_provider_id` | `UUID` | ID привязки пользователя к провайдеру |
| `provider_id` | `UUID` | ID провайдера |
| `provider_name` | `str` | Название провайдера |

## Relations

| Relation | Type | Description |
|----------|------|-------------|
| `application` | `Application \| None` | Родительская заявка |

## Create/Update Models

### Create — `ApplicationIntegrationCreate` (`src/core/models/application_integration.py`)

| Field | Type | Required | Default | Notes |
|-------|------|----------|---------|-------|
| `application_id` | `UUID` | Yes | — | FK, неизменяем |
| `user_provider_id` | `UUID` | Yes | — | |
| `provider_id` | `UUID` | Yes | — | |
| `provider_name` | `str` | Yes | — | |

### Update

Update-модель отсутствует. Записи не обновляются.

### Read — `ApplicationIntegration` (`src/core/models/application_integration.py`)

| Field | Type | Notes |
|-------|------|-------|
| `id` | `UUID` | |
| `application_id` | `UUID` | |
| `user_provider_id` | `UUID` | |
| `provider_id` | `UUID` | |
| `provider_name` | `str` | |
| `application` | `Application \| None` | Навигационное свойство |
