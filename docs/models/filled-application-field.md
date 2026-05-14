# FilledApplicationField

- **ORM file:** `src/core/models/filled_application_field.py`
- **Repo protocol:** `FilledApplicationFieldRepositoryProtocol`
- **Used by services:** `ApplicationService`

## Role
Заполненное значение кастомного поля в заявке.

## Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | `UUID` | Уникальный идентификатор |
| `value` | `str` | Введённое значение |
| `custom_field_id` | `UUID` | ID кастомного поля |
| `application_id` | `UUID` | ID заявки |

## Relations

| Relation | Type | Description |
|----------|------|-------------|
| `custom_field` | `ApplicationCustomField \| None` | Определение поля |
| `application` | `Application \| None` | Родительская заявка |

## Create/Update Models

### Create — `FilledApplicationFieldCreate` (`src/core/models/filled_application_field.py`)

| Field | Type | Required | Default | Notes |
|-------|------|----------|---------|-------|
| `value` | `str` | Yes | — | |
| `custom_field_id` | `UUID` | Yes | — | FK, неизменяем |
| `application_id` | `UUID` | Yes | — | FK, неизменяем |

### Update

Update-модель отсутствует. Записи не обновляются.

### Read — `FilledApplicationField` (`src/core/models/filled_application_field.py`)

| Field | Type | Notes |
|-------|------|-------|
| `id` | `UUID` | |
| `value` | `str` | |
| `custom_field_id` | `UUID` | |
| `application_id` | `UUID` | |
| `custom_field` | `ApplicationCustomField \| None` | Навигационное свойство |
| `application` | `Application \| None` | Навигационное свойство |
