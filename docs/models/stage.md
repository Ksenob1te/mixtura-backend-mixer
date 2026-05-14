# Stage

- **ORM file:** `src/core/models/stage.py`
- **Repo protocol:** `StageRepositoryProtocol`
- **Used by services:** `MatchService`

## Role
Этап турнира внутри bracket. Определяет формат (single elimination, round robin, swiss и т.д.) и содержит группы.

## Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | `UUID` | Уникальный идентификатор |
| `stage_index` | `int` | Порядковый номер этапа в bracket |
| `format` | `StageFormat` | Формат этапа |
| `name` | `str` | Название этапа |
| `bracket_id` | `UUID` | ID родительской сетки |

## Relations

| Relation | Type | Description |
|----------|------|-------------|
| `bracket` | `Bracket \| None` | Родительская сетка |
| `groups` | `list[StageGroup]` | Группы этапа |
| `round_robin_settings` | `RoundRobinSettings \| None` | Настройки round robin |
| `swiss_settings` | `SwissSettings \| None` | Настройки швейцарской системы |

## Create/Update Models

### Create — `StageCreate` (`src/core/models/stage.py`)

| Field | Type | Required | Default | Notes |
|-------|------|----------|---------|-------|
| `stage_index` | `int` | Yes | — | |
| `format` | `StageFormat` | Yes | — | |
| `name` | `str` | Yes | — | |
| `bracket_id` | `UUID` | Yes | — | FK, неизменяем |

### Update — `StageUpdate` (`src/core/models/stage.py`)

| Field | Type | Required | Default | Notes |
|-------|------|----------|---------|-------|
| `format` | `StageFormat \| None` | No | `None` | |
| `name` | `str \| None` | No | `None` | |

> Поля `id`, `stage_index` и `bracket_id` неизменяемы и не включены в Update-модель.

### Read — `Stage` (`src/core/models/stage.py`)

| Field | Type | Notes |
|-------|------|-------|
| `id` | `UUID` | |
| `stage_index` | `int` | |
| `format` | `StageFormat` | |
| `name` | `str` | |
| `bracket_id` | `UUID` | |
| `bracket` | `Bracket \| None` | Навигационное свойство |
| `groups` | `list[StageGroup]` | Навигационное свойство |
| `round_robin_settings` | `RoundRobinSettings \| None` | Навигационное свойство |
| `swiss_settings` | `SwissSettings \| None` | Навигационное свойство |
