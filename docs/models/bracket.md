# Bracket

- **ORM file:** `src/core/models/bracket.py`
- **Repo protocol:** `BracketRepositoryProtocol`
- **Used by services:** `MatchService`

## Role
Турнирная сетка события. Содержит stages (этапы) и placements (позиции команд).

## Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | `UUID` | Уникальный идентификатор |
| `event_id` | `UUID` | ID события |

## Relations

| Relation | Type | Description |
|----------|------|-------------|
| `event` | `Event \| None` | Родительское событие |
| `stages` | `list[Stage]` | Этапы турнира |
| `placements` | `list[BracketPlacement]` | Позиции команд |

## Create/Update Models

### Create — `BracketCreate` (`src/core/models/bracket.py`)

| Field | Type | Required | Default | Notes |
|-------|------|----------|---------|-------|
| `event_id` | `UUID` | Yes | — | FK, неизменяем |

### Update

Update-модель отсутствует. Записи не обновляются.

### Read — `Bracket` (`src/core/models/bracket.py`)

| Field | Type | Notes |
|-------|------|-------|
| `id` | `UUID` | |
| `event_id` | `UUID` | |
| `event` | `Event \| None` | Навигационное свойство |
| `stages` | `list[Stage]` | Навигационное свойство |
| `placements` | `list[BracketPlacement]` | Навигационное свойство |
