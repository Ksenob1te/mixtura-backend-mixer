# SwissSettings

- **ORM file:** `src/core/models/swiss_settings.py`
- **Repo protocol:** `SwissSettingsRepositoryProtocol`
- **Used by services:** (резерв для будущего функционала)

## Role
Настройки швейцарской системы для этапа турнира.

## Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | `UUID` | Уникальный идентификатор |
| `stage_id` | `UUID` | ID этапа |
| `score_per_win` | `int` | Очки за победу |
| `score_per_draw` | `int` | Очки за ничью |
| `score_per_bye` | `int` | Очки за bye (пропуск раунда) |

## Relations

| Relation | Type | Description |
|----------|------|-------------|
| `stage` | `Stage \| None` | Родительский этап |

## Create/Update Models

### Create — `SwissSettingsCreate` (`src/core/models/swiss_settings.py`)

| Field | Type | Required | Default | Notes |
|-------|------|----------|---------|-------|
| `stage_id` | `UUID` | Yes | — | FK, неизменяем |
| `score_per_win` | `int` | Yes | — | |
| `score_per_draw` | `int` | Yes | — | |
| `score_per_bye` | `int` | Yes | — | |

### Update — `SwissSettingsUpdate` (`src/core/models/swiss_settings.py`)

| Field | Type | Required | Default | Notes |
|-------|------|----------|---------|-------|
| `score_per_win` | `int \| None` | No | `None` | |
| `score_per_draw` | `int \| None` | No | `None` | |
| `score_per_bye` | `int \| None` | No | `None` | |

> Поле `stage_id` неизменяемо и не включено в Update-модель.

### Read — `SwissSettings` (`src/core/models/swiss_settings.py`)

| Field | Type | Notes |
|-------|------|-------|
| `id` | `UUID` | |
| `stage_id` | `UUID` | |
| `score_per_win` | `int` | |
| `score_per_draw` | `int` | |
| `score_per_bye` | `int` | |
| `stage` | `Stage \| None` | Навигационное свойство |
