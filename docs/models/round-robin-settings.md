# RoundRobinSettings

- **ORM file:** `src/core/models/round_robin_settings.py`
- **Repo protocol:** `RoundRobinSettingsRepositoryProtocol`
- **Used by services:** (резерв для будущего функционала)

## Role
Настройки round robin (каждый с каждым) для этапа турнира.

## Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | `UUID` | Уникальный идентификатор |
| `stage_id` | `UUID` | ID этапа |
| `meetings_per_pair` | `int` | Сколько раз каждая пара встречается |
| `score_system` | `str` | Система подсчёта очков |
| `score_per_win` | `int \| None` | Очки за победу |
| `score_per_draw` | `int \| None` | Очки за ничью |

## Relations

| Relation | Type | Description |
|----------|------|-------------|
| `stage` | `Stage \| None` | Родительский этап |

## Create/Update Models

### Create — `RoundRobinSettingsCreate` (`src/core/models/round_robin_settings.py`)

| Field | Type | Required | Default | Notes |
|-------|------|----------|---------|-------|
| `stage_id` | `UUID` | Yes | — | FK, неизменяем |
| `meetings_per_pair` | `int` | Yes | — | |
| `score_system` | `str` | Yes | — | |
| `score_per_win` | `int \| None` | No | `None` | |
| `score_per_draw` | `int \| None` | No | `None` | |

### Update — `RoundRobinSettingsUpdate` (`src/core/models/round_robin_settings.py`)

| Field | Type | Required | Default | Notes |
|-------|------|----------|---------|-------|
| `meetings_per_pair` | `int \| None` | No | `None` | |
| `score_system` | `str \| None` | No | `None` | |
| `score_per_win` | `int \| None` | No | `None` | |
| `score_per_draw` | `int \| None` | No | `None` | |

> Поле `stage_id` неизменяемо и не включено в Update-модель.

### Read — `RoundRobinSettings` (`src/core/models/round_robin_settings.py`)

| Field | Type | Notes |
|-------|------|-------|
| `id` | `UUID` | |
| `stage_id` | `UUID` | |
| `meetings_per_pair` | `int` | |
| `score_system` | `str` | |
| `score_per_win` | `int \| None` | |
| `score_per_draw` | `int \| None` | |
| `stage` | `Stage \| None` | Навигационное свойство |
