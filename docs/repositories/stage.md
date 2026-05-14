# StageRepository

**Protocol:** `src/core/interfaces/repo/stage.py`
**Implementation:** `src/infra/postgre/repo/stage.py`
**Model:** `Stage` ([models/stage.md](../models/stage.md))

> **Note for agents:** New repositories should inherit from `BaseRepository[Model, CreateDTO, ReadDTO, UpdateDTO]` and only override or add methods specific to the entity. See [base.md](base.md) for inherited methods.

## Base Methods

Inherited from `BaseRepository` ([base.md](base.md)):

| Method | Signature | Notes |
|--------|-----------|-------|
| `get` | `(field_id: UUID) -> Stage \| None` | Overridden with eager load flags |
| `get_list` | `(offset, limit, options, *where) -> Sequence[Stage]` | |
| `create` | `(dto: StageCreate) -> Stage` | |
| `update` | `(dto: StageUpdate) -> Stage` | |
| `delete` | `(field_id: UUID) -> bool` | |
| `exists` | `(field_id: UUID) -> bool` | |
| `count` | `(*where) -> int` | |

## Custom Methods

### `get` (overridden)

```python
async def get(
    field_id: UUID,
    load_groups: bool = False,
    load_settings: bool = False,
) -> Stage | None
```

### `list_by_bracket`

```python
async def list_by_bracket(bracket_id: UUID, offset: int, limit: int) -> Sequence[Stage]
```

Lists stages for a bracket with pagination.

## Eager Loading Map

| Flag | Relationship |
|------|-------------|
| `load_groups` | `Stage.groups` |
| `load_settings` | `Stage.round_robin_settings` + `Stage.swiss_settings` |
