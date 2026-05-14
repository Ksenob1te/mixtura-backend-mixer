# PlayerRoleRepository

**Protocol:** `src/core/interfaces/repo/player_role.py`
**Implementation:** `src/infra/postgre/repo/player_role.py`
**Model:** `PlayerRole` ([models/player-role.md](../models/player-role.md))

> **Note for agents:** New repositories should inherit from `BaseRepository[Model, CreateDTO, ReadDTO, UpdateDTO]` and only override or add methods specific to the entity. See [base.md](base.md) for inherited methods.

## Base Methods

Inherited from `BaseRepository` ([base.md](base.md)):

| Method | Signature | Notes |
|--------|-----------|-------|
| `get` | `(field_id: UUID) -> PlayerRole \| None` | Overridden with eager load flags |
| `get_list` | `(offset, limit, options, *where) -> Sequence[PlayerRole]` | |
| `create` | `(dto: PlayerRoleCreate) -> PlayerRole` | |
| `update` | `(dto: PlayerRoleUpdate) -> PlayerRole` | |
| `delete` | `(field_id: UUID) -> bool` | |
| `exists` | `(field_id: UUID) -> bool` | |
| `count` | `(*where) -> int` | |

## Custom Methods

### `get` (overridden)

```python
async def get(
    field_id: UUID,
    load_player: bool = False,
    load_game_role: bool = False,
) -> PlayerRole | None
```

### `list_by_player`

```python
async def list_by_player(player_id: UUID, offset: int, limit: int) -> Sequence[PlayerRole]
```

Lists roles for a given event player with pagination.

## Eager Loading Map

| Flag | Relationship |
|------|-------------|
| `load_player` | `PlayerRole.event_player` |
| `load_game_role` | `PlayerRole.game_role` |
