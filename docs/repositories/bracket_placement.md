# BracketPlacementRepository

**Protocol:** `src/core/interfaces/repo/bracket_placement.py`
**Implementation:** `src/infra/postgre/repo/bracket_placement.py`
**Model:** `BracketPlacement` ([models/bracket-placement.md](../models/bracket-placement.md))

> **Note for agents:** New repositories should inherit from `BaseRepository[Model, CreateDTO, ReadDTO, UpdateDTO]` and only override or add methods specific to the entity. See [base.md](base.md) for inherited methods.

## Base Methods

Inherited from `BaseRepository` ([base.md](base.md)):

| Method | Signature | Notes |
|--------|-----------|-------|
| `get` | `(field_id: UUID) -> BracketPlacement \| None` | Overridden with eager load flags |
| `get_list` | `(offset, limit, options, *where) -> Sequence[BracketPlacement]` | |
| `create` | `(dto: BracketPlacementCreate) -> BracketPlacement` | |
| `update` | `(dto: BracketPlacementUpdate) -> BracketPlacement` | |
| `delete` | `(field_id: UUID) -> bool` | |
| `exists` | `(field_id: UUID) -> bool` | |
| `count` | `(*where) -> int` | |

## Custom Methods

### `get` (overridden)

```python
async def get(field_id: UUID, load_bracket: bool) -> BracketPlacement | None
```

Note: `load_bracket` has no default — must be explicitly specified.

### `list_by_bracket`

```python
async def list_by_bracket(bracket_id: UUID) -> Sequence[BracketPlacement]
```

Returns all placements for a given bracket (no pagination).

## Eager Loading Map

| Flag | Relationship |
|------|-------------|
| `load_bracket` | `BracketPlacement.bracket` |
