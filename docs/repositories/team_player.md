# TeamPlayerRepository

**Protocol:** `src/core/interfaces/repo/team_player.py`
**Implementation:** `src/infra/postgre/repo/team_player.py`
**Model:** `TeamPlayer` ([models/team-player.md](../models/team-player.md))

> **Note for agents:** New repositories should inherit from `BaseRepository[Model, CreateDTO, ReadDTO, UpdateDTO]` and only override or add methods specific to the entity. See [base.md](base.md) for inherited methods.

## Base Methods

Inherited from `BaseRepository` ([base.md](base.md)):

| Method | Signature | Notes |
|--------|-----------|-------|
| `get` | `(field_id: UUID) -> TeamPlayer \| None` | Overridden with eager load flags |
| `get_list` | `(offset, limit, options, *where) -> Sequence[TeamPlayer]` | |
| `create` | `(dto: TeamPlayerCreate) -> TeamPlayer` | |
| `update` | `(dto: TeamPlayerUpdate) -> TeamPlayer` | |
| `delete` | `(field_id: UUID) -> bool` | |
| `exists` | `(field_id: UUID) -> bool` | |
| `count` | `(*where) -> int` | |

## Custom Methods

### `get` (overridden)

```python
async def get(
    field_id: UUID,
    load_team: bool = False,
    load_role: bool = False,
) -> TeamPlayer | None
```

### `list_by_team`

```python
async def list_by_team(team_id: UUID) -> Sequence[TeamPlayer]
```

Returns all players for a given team (no pagination).

## Eager Loading Map

| Flag | Relationship |
|------|-------------|
| `load_team` | `TeamPlayer.team` |
| `load_role` | `TeamPlayer.game_role` |
