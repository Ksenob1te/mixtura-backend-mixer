# TeamFormationVariantStore

**Protocol:** `src/core/interfaces/repo/team_formation_variant.py`
**Implementation:** `src/infra/redis/team_formation.py`
**Model:** `TeamFormationJob` (`src/core/results/team_formation.py`)

Redis-хранилище результатов балансировки команд. Хранит `TeamFormationJob` с вариантами распределения игроков по командам. Поддерживает паттерн «latest pointer» — отдельный ключ, указывающий на последний сохранённый job для пары `(event_id, draft_id)`.

**Формат ключей:**
- `event:{event_id}:draft:{draft_id}:team_formation:{job_id}` — данные конкретного job
- `event:{event_id}:draft:{draft_id}:team_formation:latest` — указатель на последний `job_id`

## Custom Methods

### `save`

```python
async def save(job_id: UUID, event_id: UUID, draft_id: UUID, payload: TeamFormationJob, ttl_seconds: int) -> None
```

Сохраняет `TeamFormationJob` и обновляет latest-указатель. `ttl_seconds` — время жизни ключей в секундах.

### `get`

```python
async def get(job_id: UUID, event_id: UUID, draft_id: UUID) -> TeamFormationJob | None
```

Возвращает job по точному `job_id` или `None`.

### `get_latest_by_draft`

```python
async def get_latest_by_draft(event_id: UUID, draft_id: UUID) -> TeamFormationJob | None
```

Возвращает последний сохранённый job для заданных `event_id` и `draft_id`. Использует latest-указатель для определения актуального `job_id`. Возвращает `None`, если указатель отсутствует, содержит невалидный UUID или данные job не найдены.

### `delete`

```python
async def delete(job_id: UUID, event_id: UUID, draft_id: UUID) -> None
```

Удаляет данные конкретного job из Redis (latest-указатель остаётся).

## Used By

- `TeamFormationService` — `save()` при создании pending job, `get()` / `get_latest_by_draft()` при чтении, `delete()` при выборе варианта.
