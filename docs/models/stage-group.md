# StageGroup

- **ORM file:** `src/core/models/stage_group.py`
- **Repo protocol:** `StageGroupRepositoryProtocol`
- **Used by services:** `MatchService`

## Role
Группа внутри этапа турнира. Содержит матчи данного этапа.

## Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | `UUID` | Уникальный идентификатор |
| `stage_id` | `UUID` | ID родительского этапа |
| `name` | `str` | Название группы |
| `advance_count` | `int \| None` | Сколько команд в каждой группе проходит дальше |

## Relations

| Relation | Type | Description |
|----------|------|-------------|
| `stage` | `Stage \| None` | Родительский этап |
| `matches` | `list[Match]` | Матчи группы |

## Create/Update Models

### Create — `StageGroupCreate` (`src/core/models/stage_group.py`)

| Field | Type | Required | Default | Notes |
|-------|------|----------|---------|-------|
| `stage_id` | `UUID` | Yes | — | FK, неизменяем |
| `name` | `str` | Yes | — | |
| `advance_count` | `int \| None` | No | `None` | |

### Update — `StageGroupUpdate` (`src/core/models/stage_group.py`)

| Field | Type | Required | Default | Notes |
|-------|------|----------|---------|-------|
| `name` | `str \| None` | No | `None` | |
| `advance_count` | `int \| None` | No | `None` | |

> Поле `stage_id` неизменяемо и не включено в Update-модель.

### Read — `StageGroup` (`src/core/models/stage_group.py`)

| Field | Type | Notes |
|-------|------|-------|
| `id` | `UUID` | |
| `stage_id` | `UUID` | |
| `name` | `str` | |
| `advance_count` | `int \| None` | |
| `stage` | `Stage \| None` | Навигационное свойство |
| `matches` | `list[Match]` | Навигационное свойство |
