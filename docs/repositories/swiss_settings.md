# SwissSettingsRepository

**Protocol:** `src/core/interfaces/repo/swiss_settings.py`
**Implementation:** `src/infra/postgre/repo/swiss_settings.py`
**Model:** `SwissSettings` ([models/swiss-settings.md](../models/swiss-settings.md))

> **Note for agents:** New repositories should inherit from `BaseRepository[Model, CreateDTO, ReadDTO, UpdateDTO]` and only override or add methods specific to the entity. See [base.md](base.md) for inherited methods.

## Base Methods

Inherited from `BaseRepository` ([base.md](base.md)):

| Method | Signature | Notes |
|--------|-----------|-------|
| `get` | `(field_id: UUID) -> SwissSettings \| None` | |
| `get_list` | `(offset, limit, options, *where) -> Sequence[SwissSettings]` | |
| `create` | `(dto: SwissSettingsCreate) -> SwissSettings` | |
| `update` | `(dto: SwissSettingsUpdate) -> SwissSettings` | |
| `delete` | `(field_id: UUID) -> bool` | |
| `exists` | `(field_id: UUID) -> bool` | |
| `count` | `(*where) -> int` | |

## Custom Methods

### `get_by_stage_id`

```python
async def get_by_stage_id(stage_id: UUID, load_stage: bool) -> SwissSettings | None
```

Finds Swiss settings by stage ID. Note: `load_stage` has no default — must be explicitly specified.

### `delete_by_stage`

```python
async def delete_by_stage(stage_id: UUID) -> None
```

Deletes Swiss settings for a given stage. Returns `None` (not `bool`).

## Eager Loading Map

| Flag | Relationship |
|------|-------------|
| `load_stage` | `SwissSettings.stage` |
