# BalancerTaskStore

**Protocol:** `src/core/interfaces/repo/balancer_task.py`
**Implementation:** `src/infra/redis/balancer_task.py`
**Model:** `BalancerTask` (`src/core/results/balancer_task.py`)

Redis-хранилище контекста задач балансировки. Ключи имеют вид `balancer_task:{task_id}`, значения сериализуются через `model_dump_json()` / `model_validate_json()`, TTL задаётся при сохранении.

## Custom Methods

### `save`

```python
async def save(task: BalancerTask, ttl_seconds: int) -> None
```

Сохраняет задачу в Redis с TTL. `ttl_seconds` — время жизни ключа в секундах.

### `get`

```python
async def get(task_id: UUID) -> BalancerTask | None
```

Возвращает задачу по `task_id` или `None`, если ключ не найден или истёк.

### `delete`

```python
async def delete(task_id: UUID) -> None
```

Удаляет ключ задачи из Redis.

## Used By

- `TeamFormationService` — сохранение контекста при `run()`, чтение при `complete_formation()`, удаление после завершения.
