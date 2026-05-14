# MatchScoreRepository

**Protocol:** `src/core/interfaces/repo/match_score.py`
**Implementation:** `src/infra/postgre/repo/match_score.py`
**Model:** `MatchScore` ([models/match-score.md](../models/match-score.md))

> **Note for agents:** New repositories should inherit from `BaseRepository[Model, CreateDTO, ReadDTO, UpdateDTO]` and only override or add methods specific to the entity. See [base.md](base.md) for inherited methods.

## Base Methods

Inherited from `BaseRepository` ([base.md](base.md)):

| Method | Signature | Notes |
|--------|-----------|-------|
| `get` | `(field_id: UUID) -> MatchScore \| None` | Overridden with eager load flags |
| `get_list` | `(offset, limit, options, *where) -> Sequence[MatchScore]` | |
| `create` | `(dto: MatchScoreCreate) -> MatchScore` | |
| `update` | `(score_id: UUID, dto: MatchScoreUpdate) -> MatchScore` | Takes `score_id` separately |
| `delete` | `(field_id: UUID) -> bool` | |
| `exists` | `(field_id: UUID) -> bool` | |
| `count` | `(*where) -> int` | |

## Custom Methods

### `get` (overridden)

```python
async def get(
    field_id: UUID,
    load_slot: bool = False,
    load_team: bool = False,
) -> MatchScore | None
```

### `get_by_slot_id`

```python
async def get_by_slot_id(
    slot_id: UUID,
    load_slot: bool,
    load_team: bool,
) -> MatchScore | None
```

Finds score by slot ID with optional eager loading.

## Eager Loading Map

| Flag | Relationship |
|------|-------------|
| `load_slot` | `MatchScore.slot` |
| `load_team` | `MatchScore.team` |
