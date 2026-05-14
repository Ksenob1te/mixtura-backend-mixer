# SelectedGameRoleRepository

**Protocol:** `src/core/interfaces/repo/selected_game_role.py`
**Implementation:** `src/infra/postgre/repo/selected_game_role.py`
**Model:** `SelectedGameRole` ([models/selected-game-role.md](../models/selected-game-role.md))

> **Note for agents:** New repositories should inherit from `BaseRepository[Model, CreateDTO, ReadDTO, UpdateDTO]` and only override or add methods specific to the entity. See [base.md](base.md) for inherited methods.

## Base Methods

Inherited from `BaseRepository` ([base.md](base.md)):

| Method | Signature | Notes |
|--------|-----------|-------|
| `get` | `(field_id: UUID) -> SelectedGameRole \| None` | Overridden with eager load flags |
| `get_list` | `(offset, limit, options, *where) -> Sequence[SelectedGameRole]` | |
| `create` | `(dto: SelectedGameRoleCreate) -> SelectedGameRole` | |
| `update` | `(dto: SelectedGameRoleUpdate) -> SelectedGameRole` | |
| `delete` | `(field_id: UUID) -> bool` | |
| `exists` | `(field_id: UUID) -> bool` | |
| `count` | `(*where) -> int` | |

## Custom Methods

### `get` (overridden)

```python
async def get(
    field_id: UUID,
    load_player_roles: bool,
    load_team_players: bool,
) -> SelectedGameRole | None
```

Note: `load_player_roles` and `load_team_players` have no defaults — must be explicitly specified.

### `list_by_event`

```python
async def list_by_event(event_id: UUID) -> Sequence[SelectedGameRole]
```

Returns all selected game roles for a given event (no pagination).

## Eager Loading Map

| Flag | Relationship |
|------|-------------|
| `load_player_roles` | `SelectedGameRole.player_roles` |
| `load_team_players` | `SelectedGameRole.team_players` |
