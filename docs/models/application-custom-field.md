# ApplicationCustomField

- **ORM file:** `src/core/models/application_custom_field.py`
- **Repo protocol:** `ApplicationCustomFieldRepositoryProtocol`
- **Used by services:** `SettingsService`, `ApplicationService`

## Role
Кастомное поле формы заявки. Определяет, какие дополнительные данные нужно собрать от участников.
Является одной из настроек для заявок.

## Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | `UUID` | Уникальный идентификатор |
| `event_id` | `UUID` | ID события |
| `name` | `str` | Название поля |
| `is_private` | `bool` | Видимо только организаторам |
| `is_required` | `bool` | Обязательно для заполнения |

## Relations

| Relation | Type | Description |
|----------|------|-------------|
| `event` | `Event \| None` | Родительское событие |

## Create/Update Models

### Create — `ApplicationCustomFieldCreate` (`src/core/models/application_custom_field.py`)

| Field | Type | Required | Default | Notes |
|-------|------|----------|---------|-------|
| `event_id` | `UUID` | Yes | — | FK, неизменяем |
| `name` | `str` | Yes | — | |
| `is_private` | `bool` | No | `False` | |
| `is_required` | `bool` | No | `False` | |

### Update — `ApplicationCustomFieldUpdate` (`src/core/models/application_custom_field.py`)

| Field | Type | Required | Default | Notes |
|-------|------|----------|---------|-------|
| `name` | `str \| None` | No | `None` | |
| `is_private` | `bool \| None` | No | `None` | |
| `is_required` | `bool \| None` | No | `None` | |

> Поля `id` и `event_id` неизменяемы и не включены в Update-модель.

### Read — `ApplicationCustomField` (`src/core/models/application_custom_field.py`)

| Field | Type | Notes |
|-------|------|-------|
| `id` | `UUID` | |
| `event_id` | `UUID` | |
| `name` | `str` | |
| `is_private` | `bool` | |
| `is_required` | `bool` | |
| `event` | `Event \| None` | Навигационное свойство |
