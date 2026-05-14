# Organizer

- **ORM file:** `src/core/models/organizer.py`
- **Repo protocol:** `OrganizerRepositoryProtocol`
- **Used by services:** `EventService`, `OrganizerService`, `ApplicationService`, `DraftService`, `PlayerService`, `TeamFormationService`, `MatchService`, `SettingsService`

## Role
Организатор события. Member с этой записью имеет полные права на управление событием без необходимости permission битов.

## Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | `UUID` | Уникальный идентификатор |
| `event_id` | `UUID` | ID события |
| `member_id` | `UUID` | ID участника-организатора |

## Relations

| Relation | Type | Description |
|----------|------|-------------|
| `event` | `Event \| None` | Родительское событие |

## Create/Update Models

### Create — `OrganizerCreate` (`src/core/models/organizer.py`)

| Field | Type | Required | Default | Notes |
|-------|------|----------|---------|-------|
| `event_id` | `UUID` | Yes | — | FK, неизменяем |
| `member_id` | `UUID` | Yes | — | |

### Update

Update-модель отсутствует. Записи не обновляются.

### Read — `Organizer` (`src/core/models/organizer.py`)

| Field | Type | Notes |
|-------|------|-------|
| `id` | `UUID` | |
| `event_id` | `UUID` | |
| `member_id` | `UUID` | |
| `event` | `Event \| None` | Навигационное свойство |
