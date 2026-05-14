# Application

- **ORM file:** `src/core/models/application.py`
- **Repo protocol:** `ApplicationRepositoryProtocol`
- **Used by services:** `ApplicationService`

## Role
Заявка на участие в событии. К этой модели отдельньыми моедлями привязываются заполненные поля, интеграции и роли.

## Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | `UUID` | Уникальный идентификатор |
| `event_id` | `UUID` | ID события |
| `member_id` | `UUID` | ID заявителя |
| `status` | `ApplicationStatus` | Текущий статус (`PENDING`/`APPROVED`/`REJECTED`/`WAITLIST`) |
| `created_at` | `datetime` | Время создания |

## Relations

| Relation | Type | Description |
|----------|------|-------------|
| `event` | `Event \| None` | Родительское событие |
| `integrations` | `list[ApplicationIntegration]` | Привязанные интеграции |
| `filled_fields` | `list[FilledApplicationField]` | Заполненные кастомные поля |
| `event_player` | `EventPlayer \| None` | Связанный участник (если approved) |

## Create/Update Models

### Create — `ApplicationCreate` (`src/core/models/application.py`)

| Field | Type | Required | Default | Notes |
|-------|------|----------|---------|-------|
| `event_id` | `UUID` | Yes | — | FK, неизменяем |
| `member_id` | `UUID` | Yes | — | FK, неизменяем |
| `status` | `ApplicationStatus` | No | `ApplicationStatus.PENDING` | |

### Update — `ApplicationUpdate` (`src/core/models/application.py`)

| Field | Type | Required | Default | Notes |
|-------|------|----------|---------|-------|
| `status` | `ApplicationStatus \| None` | No | `None` | |

> Поля `id`, `event_id`, `member_id` и `created_at` неизменяемы и не включены в Update-модель.

### Read — `Application` (`src/core/models/application.py`)

| Field | Type | Notes |
|-------|------|-------|
| `id` | `UUID` | |
| `event_id` | `UUID` | |
| `member_id` | `UUID` | |
| `status` | `ApplicationStatus` | |
| `created_at` | `datetime` | |
| `event` | `Event \| None` | Навигационное свойство |
| `integrations` | `list[ApplicationIntegration]` | Навигационное свойство |
| `filled_fields` | `list[FilledApplicationField]` | Навигационное свойство |
| `event_player` | `EventPlayer \| None` | Навигационное свойство |
