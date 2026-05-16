# RatingClient

**Protocol:** `src/core/interfaces/repo/rating.py`
**Implementation:** `src/infra/clients/rating.py`

Клиент для взаимодействия с mixtura-ranker. Поддерживает два режима:
- **RPC (блокирующий):** `calculate_effective_ratings()` — запрос-ответ через `RabbitRpcClient`
- **Publish (fire-and-forget):** `process_match_result()` — публикация результата матча без ожидания ответа

## Custom Methods

### `calculate_effective_ratings`

```python
async def calculate_effective_ratings(
    draft_id: UUID,
    players: list[RatingPlayerRequest],
    settings: RatingSettings | None = None,
) -> list[PlayerEffectiveRating]
```

Вычисляет эффективные рейтинги игроков через RPC-вызов очереди `rating.effective.calculate`.

**Параметры:**
- `draft_id` — ID драфта
- `players` — список `RatingPlayerRequest` (member_id, role_id, open_rating, priority)
- `settings` — параметры рейтинговой системы (RatingSettings, с `extra="allow"`)

**Возвращает:** список `PlayerEffectiveRating` (member_id, role_id, open_rating, effective_rating, hidden_rating).

### `process_match_result`

```python
async def process_match_result(
    match_id: UUID,
    match_time: str,
    teams: list[MatchTeamInput],
    team_ranks: list[float],
    players: list[MatchPlayerInput],
    settings: RatingSettings | None = None,
) -> None
```

Публикует результат матча в очередь `rating.match.process` (fire-and-forget).

**Параметры:**
- `match_id` — ID матча
- `match_time` — время матча (ISO строка)
- `teams` — список `MatchTeamInput` (team_id, player_ids)
- `team_ranks` — ранги команд
- `players` — список `MatchPlayerInput` (member_id, role_id, open_rating)
- `settings` — параметры рейтинговой системы (RatingSettings, с `extra="allow"`)

## Serialization

Модели сериализуются в JSON-словари через `model_dump(mode="json")` перед отправкой по RabbitMQ. Ответ десериализуется в `PlayerEffectiveRating` через конструктор `PlayerEffectiveRating(**raw_player)`.

## Used By

- `TeamFormationService` — `calculate_effective_ratings()` при `run()`
- `MatchService` — `process_match_result()` при `record_result()`
