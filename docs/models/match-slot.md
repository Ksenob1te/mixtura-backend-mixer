# MatchSlot

- **ORM file:** `src/core/models/match_slot.py`
- **Repo protocol:** `MatchSlotRepositoryProtocol`
- **Used by services:** `MatchService`

## Role
Слот матча — позиция для команды в матче. Определяет, как команда попадает в матч (ручное назначение, победитель другого матча, место в группе).

## Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | `UUID` | Уникальный идентификатор |
| `match_id` | `UUID` | ID матча |
| `slot_num` | `int` | Номер слота (1, 2, ...) |
| `source_type` | `MatchSlotSourceType` | Источник команды: `WINNER_OF`, `LOSER_OF`, `GROUP_PLACEMENT`, `MANUAL`, `AUTO` |
| `source_match_id` | `UUID \| None` | ID матча-источника (для `WINNER_OF`/`LOSER_OF`) |
| `source_group_id` | `UUID \| None` | ID группы-источника (для `GROUP_PLACEMENT`) |
| `group_placement` | `int \| None` | Место в группе (для `GROUP_PLACEMENT`) |

## Relations

| Relation | Type | Description |
|----------|------|-------------|
| `match` | `Match \| None` | Родительский матч |
| `source_match` | `Match \| None` | Матч-источник |
| `source_group` | `StageGroup \| None` | Группа-источник |
| `score` | `MatchScore \| None` | Счёт команды в этом слоте |

## Create/Update Models

### Create — `MatchSlotCreate` (`src/core/models/match_slot.py`)

| Field | Type | Required | Default | Notes |
|-------|------|----------|---------|-------|
| `match_id` | `UUID` | Yes | — | FK, неизменяем |
| `slot_num` | `int` | Yes | — | |
| `source_type` | `MatchSlotSourceType` | Yes | — | |
| `source_match_id` | `UUID \| None` | No | `None` | |
| `source_group_id` | `UUID \| None` | No | `None` | |
| `group_placement` | `int \| None` | No | `None` | |

### Update

Update-модель отсутствует. Записи не обновляются.

### Read — `MatchSlot` (`src/core/models/match_slot.py`)

| Field | Type | Notes |
|-------|------|-------|
| `id` | `UUID` | |
| `match_id` | `UUID` | |
| `slot_num` | `int` | |
| `source_type` | `MatchSlotSourceType` | |
| `source_match_id` | `UUID \| None` | |
| `source_group_id` | `UUID \| None` | |
| `group_placement` | `int \| None` | |
| `match` | `Match \| None` | Навигационное свойство |
| `source_match` | `Match \| None` | Навигационное свойство |
| `source_group` | `StageGroup \| None` | Навигационное свойство |
| `score` | `MatchScore \| None` | Навигационное свойство |
