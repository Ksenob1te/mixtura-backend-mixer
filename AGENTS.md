# Repository Instructions

## Commands
- Use `uv` with Python `>=3.13`; `uv run ...` creates/uses the local `.venv` from `uv.lock`.
- Install/sync dependencies: `uv sync`.
- Typecheck: `uv run mypy src`.
- Test suite: `uv run pytest`; focused test form is `uv run pytest tests/path.py::test_name`.
- Dev services: `docker compose -f docker-compose.dev.yaml up -d postgres redis`; set `POSTGRES_PASSWORD` and keep `POSTGRES_DB` consistent with the app env.

## Current Baseline
- `uv run pytest --collect-only` currently fails in `tests/conftest.py`: it imports legacy `Server`, `GameRoleSet`, etc. from `src.infra.postgre.models`.
- `uv run mypy src` currently fails on legacy `src.domain.*` imports and unsuffixed model imports from `src.infra.postgre.models`.
- Do not assume the Docker entrypoint starts the app: it calls missing `src.infra.static`; `start.py` imports missing `src.domain.main`.
- Do not preserve backward compatibility with legacy service/domain code unless explicitly requested; remove or rewrite stale paths instead of adding aliases/shims.

## Code Structure And Naming
- One domain entity is usually mirrored across four files with the same snake_case name: DTO/enums in `src/core/models/<entity>.py`, repo protocol in `src/core/interfaces/repo/<entity>.py`, ORM model in `src/infra/postgre/models/<entity>.py`, repo implementation in `src/infra/postgre/repo/<entity>.py`.
- DTO classes use unsuffixed PascalCase names (`Application`, `Event`, `Draft`) and live in `src.core.models`; ORM classes use `*Model` names (`ApplicationModel`, `EventModel`) and live in `src.infra.postgre.models`.
- Do not add unsuffixed ORM aliases to `src.infra.postgre.models` to satisfy stale code; fix imports to `src.core.models` for DTO/enums or to explicit `*Model` classes for SQLAlchemy.
- `src/core/models/__init__.py` is empty; import DTOs/enums from concrete modules such as `src.core.models.event`, not from the package root.
- `src/infra/postgre/models/__init__.py` and `src/infra/postgre/repo/__init__.py` are export barrels for `*Model` and `*Repository` classes.
- Table names are explicit `'<entity>_table'` strings; relationships use `lazy="raise"`, so repository `get(...)` methods expose `load_*` flags and add `selectinload(...)` options.
- Repositories inherit `BaseRepository[Model, DTO]`, set `model` and `dto_model`, and convert ORM objects with `dto_model.model_validate(..., from_attributes=True)`.
- Repository interfaces are `typing.Protocol`s under `src.core.interfaces.repo`; services should depend on repository methods and DTOs, not on ORM model classes.
- `src.core.service` holds business logic, but current service files still contain stale `src.domain.*` imports and some unsuffixed `src.infra.postgre.models` imports.
- Event status transitions are loaded from `src/config/event_flow.ini` by `src.env_config.EventFlowConfig`; update the INI when changing event states or allowed transitions.

## Database And Migrations
- Runtime DB settings come from `src.env_config` environment aliases, not from `alembic.ini`; Alembic sets `sqlalchemy.url` from `env.postgres.url` in `alembic/env.py`.
- `docker-compose.dev.yaml` defaults `POSTGRES_DB` to `mixtura-mixer`, while `src.env_config.PostgresConfig` defaults to `mixtura-auth`; set env vars explicitly when running migrations/tests against compose.
- Alembic migrations are async and stored in `alembic/versions`; current chain has an empty base revision followed by the schema revision.

## Testing Notes
- `pytest.ini` sets `asyncio_mode = auto` and points dotenv loading at `.env`.
- The test fixture uses `testcontainers.postgres.PostgresContainer("postgres:15")`, so any real test run will require Docker once the stale imports are fixed.
