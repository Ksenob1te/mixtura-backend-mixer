# BaseRepository

**Implementation:** `src/infra/postgre/repo/base.py`

Generic CRUD base class for all repositories. Uses SQLAlchemy async session and Pydantic DTOs.

## Generics

| TypeVar | Bound | Purpose |
|---------|-------|---------|
| `ModelType` | `Base` (SQLAlchemy ORM) | Database model class |
| `CreateDTO` | `BaseModel` | DTO for create operations |
| `ReadDTO` | `BaseModel` | DTO returned by all read operations |
| `UpdateDTO` | `BaseModel` | DTO for update operations |

## Methods

| Method | Signature | Notes |
|--------|-----------|-------|
| `get` | `(field_id: UUID) -> ReadDTO \| None` | Lookup by `id` column |
| `get_list` | `(offset, limit, options, *where, order_by) -> Sequence[ReadDTO]` | Generic filtered list with pagination |
| `create` | `(dto: CreateDTO) -> ReadDTO` | Maps DTO fields to model columns, flushes, refreshes |
| `update` | `(dto: UpdateDTO) -> ReadDTO` | Uses `exclude_unset=True` for partial updates, `merge()` |
| `delete` | `(field_id: UUID) -> bool` | Returns `True` if row existed and was deleted |
| `exists` | `(field_id: UUID) -> bool` | `SELECT count(*) WHERE id = ?` |
| `count` | `(*where) -> int` | `SELECT count(*)` with optional filters |

## Internal Methods

| Method | Purpose |
|--------|---------|
| `_flush` | Wraps `session.flush()`, converts SQLAlchemy `IntegrityError` to domain exceptions |
| `_get_model` | Fetches ORM object by ID with optional `options` (eager loads) |
| `_to_dto` | Converts ORM object to `ReadDTO` via `model_validate(from_attributes=True)` |
| `_get` | Combines `_get_model` + `_to_dto` |
| `_list_model` | Builds `select()` with pagination, filters, options, ordering — returns ORM objects |
| `_dto_to_data` | Extracts dict from DTO, filters to only model column names |

## Integrity Error Handling (`_flush`)

| SQL State | Domain Exception | Meaning |
|-----------|-----------------|---------|
| `23503` | `IntegrityForeignException` | Foreign key violation |
| `23505` | `IntegrityUniqueException` | Unique constraint violation |
| Other | `IntegrityUnknownException` | Other integrity error |

## DTO Mapping (`_dto_to_data`)

Filters DTO fields to only those that exist as columns on the ORM model. Supports Pydantic `model_dump()`, `Mapping`, and plain objects. When `exclude_unset=True` (used in `update`), only explicitly set fields are included.
