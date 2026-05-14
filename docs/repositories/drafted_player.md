# DraftedPlayerRepository

**Protocol:** `src/core/interfaces/repo/drafted_player.py`
**Implementation:** `src/infra/postgre/repo/drafted_player.py`
**Model:** `DraftedPlayer` ([models/drafted-player.md](../models/drafted-player.md))

> **Note for agents:** New repositories should inherit from `BaseRepository[Model, CreateDTO, ReadDTO, UpdateDTO]` and only override or add methods specific to the entity. See [base.md](base.md) for inherited methods.

## Base Methods

Inherited from `BaseRepository` ([base.md](base.md)):

| Method | Signature | Notes |
|--------|-----------|-------|
| `get` | `(field_id: UUID) -> DraftedPlayer \| None` | Overridden with eager load flags |
| `get_list` | `(offset, limit, options, *where) -> Sequence[DraftedPlayer]` | |
| `create` | `(dto: DraftedPlayerCreate) -> DraftedPlayer` | |
| `update` | `(dto: DraftedPlayerCreate) -> DraftedPlayer` | Uses `DraftedPlayerCreate` for both create and update |
| `delete` | `(field_id: UUID) -> bool` | |
| `exists` | `(field_id: UUID) -> bool` | |
| `count` | `(*where) -> int` | |

## Custom Methods

### `get` (overridden)

```python
async def get(
    field_id: UUID,
    load_draft: bool = False,
    load_player: bool = False,
) -> DraftedPlayer | None
```

### `list_by_draft`

```python
async def list_by_draft(draft_id: UUID) -> Sequence[DraftedPlayer]
```

Returns all drafted players for a given draft (no pagination).

## Eager Loading Map

| Flag | Relationship |
|------|-------------|
| `load_draft` | `DraftedPlayer.draft` |
| `load_player` | `DraftedPlayer.event_player` |
