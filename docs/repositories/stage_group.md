# StageGroupRepository

**Protocol:** `src/core/interfaces/repo/stage_group.py`
**Implementation:** `src/infra/postgre/repo/stage_group.py`
**Model:** `StageGroup` ([models/stage-group.md](../models/stage-group.md))

> **Note for agents:** New repositories should inherit from `BaseRepository[Model, CreateDTO, ReadDTO, UpdateDTO]` and only override or add methods specific to the entity. See [base.md](base.md) for inherited methods.

## Base Methods

Inherited from `BaseRepository` ([base.md](base.md)):

| Method | Signature | Notes |
|--------|-----------|-------|
| `get` | `(field_id: UUID) -> StageGroup \| None` | Overridden with eager load flags |
| `get_list` | `(offset, limit, options, *where) -> Sequence[StageGroup]` | |
| `create` | `(dto: StageGroupCreate) -> StageGroup` | |
| `update` | `(dto: StageGroupUpdate) -> StageGroup` | |
| `delete` | `(field_id: UUID) -> bool` | |
| `exists` | `(field_id: UUID) -> bool` | |
| `count` | `(*where) -> int` | |

## Custom Methods

### `get` (overridden)

```python
async def get(field_id: UUID, load_matches: bool = False) -> StageGroup | None
```

### `list_by_stage`

```python
async def list_by_stage(stage_id: UUID) -> Sequence[StageGroup]
```

Returns all groups for a given stage (no pagination).

## Eager Loading Map

| Flag | Relationship |
|------|-------------|
| `load_matches` | `StageGroup.matches` |
