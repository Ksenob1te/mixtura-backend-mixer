# PlayerRepository

**Protocol:** `src/core/interfaces/repo/player.py`
**Implementation:** `src/infra/postgre/repo/player.py`
**Model:** `EventPlayer` ([models/event-player.md](../models/event-player.md))

> **Note for agents:** New repositories should inherit from `BaseRepository[Model, CreateDTO, ReadDTO, UpdateDTO]` and only override or add methods specific to the entity. See [base.md](base.md) for inherited methods.

## Base Methods

Inherited from `BaseRepository` ([base.md](base.md)):

| Method | Signature | Notes |
|--------|-----------|-------|
| `get` | `(field_id: UUID) -> EventPlayer \| None` | Overridden with eager load flags |
| `get_list` | `(offset, limit, options, *where) -> Sequence[EventPlayer]` | |
| `create` | `(dto: EventPlayerCreate) -> EventPlayer` | |
| `update` | `(player_id: UUID, dto: EventPlayerUpdate) -> EventPlayer` | Takes `player_id` separately |
| `delete` | `(field_id: UUID) -> bool` | |
| `exists` | `(field_id: UUID) -> bool` | |
| `count` | `(*where) -> int` | |

## Custom Methods

### `get` (overridden)

```python
async def get(
    field_id: UUID,
    load_roles: bool = False,
    load_drafted: bool = False,
) -> EventPlayer | None
```

### `get_by_event_and_member`

```python
async def get_by_event_and_member(event_id: UUID, member_id: UUID) -> EventPlayer | None
```

Finds event player by event and member pair.

### `list_by_event`

```python
async def list_by_event(
    event_id: UUID,
    offset: int,
    limit: int,
    status: EventPlayerStatus | None = None,
) -> Sequence[EventPlayer]
```

Lists event players with optional status filter.

### `list_by_event_with_roles`

```python
async def list_by_event_with_roles(event_id: UUID) -> Sequence[EventPlayer]
```

Lists all event players for an event with their roles eagerly loaded (no pagination).

### `list_by_ids`

```python
async def list_by_ids(event_id: UUID, player_ids: list[UUID]) -> Sequence[EventPlayer]
```

Returns only players matching both the given `event_id` and whose `id` is in `player_ids`. Returns empty list if `player_ids` is empty.

## Eager Loading Map

| Flag | Relationship |
|------|-------------|
| `load_roles` | `EventPlayer.player_roles` |
| `load_drafted` | `EventPlayer.drafted_players` |
