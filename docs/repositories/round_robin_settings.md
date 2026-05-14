# RoundRobinSettingsRepository

**Protocol:** `src/core/interfaces/repo/round_robin_settings.py`
**Implementation:** `src/infra/postgre/repo/round_robin_settings.py`
**Model:** `RoundRobinSettings` ([models/round-robin-settings.md](../models/round-robin-settings.md))

> **Note for agents:** New repositories should inherit from `BaseRepository[Model, CreateDTO, ReadDTO, UpdateDTO]` and only override or add methods specific to the entity. See [base.md](base.md) for inherited methods.

## Base Methods

Inherited from `BaseRepository` ([base.md](base.md)):

| Method | Signature | Notes |
|--------|-----------|-------|
| `get` | `(field_id: UUID) -> RoundRobinSettings \| None` | |
| `get_list` | `(offset, limit, options, *where) -> Sequence[RoundRobinSettings]` | |
| `create` | `(dto: RoundRobinSettingsCreate) -> RoundRobinSettings` | |
| `update` | `(dto: RoundRobinSettingsUpdate) -> RoundRobinSettings` | |
| `delete` | `(field_id: UUID) -> bool` | |
| `exists` | `(field_id: UUID) -> bool` | |
| `count` | `(*where) -> int` | |

## Custom Methods

### `get_by_stage_id`

```python
async def get_by_stage_id(stage_id: UUID, load_stage: bool) -> RoundRobinSettings | None
```

Finds Round Robin settings by stage ID. Note: `load_stage` has no default — must be explicitly specified.

### `delete_by_stage`

```python
async def delete_by_stage(stage_id: UUID) -> None
```

Deletes Round Robin settings for a given stage. Returns `None` (not `bool`).

## Eager Loading Map

| Flag | Relationship |
|------|-------------|
| `load_stage` | `RoundRobinSettings.stage` |
