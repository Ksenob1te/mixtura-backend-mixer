# BracketPlacement

- **ORM file:** `src/core/models/bracket_placement.py`
- **Repo protocol:** `BracketPlacementRepositoryProtocol`
- **Used by services:** (резерв для будущего функционала)

## Role
Позиция команды в турнирной сетке. Определяет стартовое место команды в bracket.

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
