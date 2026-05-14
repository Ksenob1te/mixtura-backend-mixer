# BracketPlacement

- **ORM file:** `src/core/models/bracket_placement.py`
- **Repo protocol:** `BracketPlacementRepositoryProtocol`
- **Used by services:** (резерв для будущего функционала)

## Role
Позиция команды в турнирной сетке. Определяет финальное место команды в bracket. Поле `placement` хранит наивысшее место из диапазона — если несколько команд делят места, все они получают наивысшее место из спектра, а следующие команды идут со смещением на количество tied-команд.

Пример:
```
1. Команда А — placement = 1
2. Команда Б — placement = 2
3. Команда В — placement = 2  (делят 2-3 места, обе получают 2)
4. Команда Г — placement = 4  (смещение на 2 tied-команды)
```

## Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | `UUID` | Уникальный идентификатор |
| `bracket_id` | `UUID` | ID сетки |
| `team_id` | `UUID` | ID команды |
| `placement` | `int` | Порядковый номер позиции |

## Relations

| Relation | Type | Description |
|----------|------|-------------|
| `bracket` | `Bracket \| None` | Родительская сетка |
| `team` | `Team \| None` | Команда |

## Create/Update Models

### Create — `BracketPlacementCreate` (`src/core/models/bracket_placement.py`)

| Field | Type | Required | Default | Notes |
|-------|------|----------|---------|-------|
| `bracket_id` | `UUID` | Yes | — | FK, неизменяем |
| `team_id` | `UUID` | Yes | — | FK |
| `placement` | `int` | Yes | — | |

### Update — `BracketPlacementUpdate` (`src/core/models/bracket_placement.py`)

| Field | Type | Required | Default | Notes |
|-------|------|----------|---------|-------|
| `team_id` | `UUID \| None` | No | `None` | |
| `placement` | `int \| None` | No | `None` | |

> Поле `bracket_id` неизменяемо и не включено в Update-модель.

### Read — `BracketPlacement` (`src/core/models/bracket_placement.py`)

| Field | Type | Notes |
|-------|------|-------|
| `id` | `UUID` | |
| `bracket_id` | `UUID` | |
| `team_id` | `UUID` | |
| `placement` | `int` | |
| `bracket` | `Bracket \| None` | Навигационное свойство |
| `team` | `Team \| None` | Навигационное свойство |
