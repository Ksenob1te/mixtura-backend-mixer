# BalancerRequestRepository

**Protocol:** `src/core/interfaces/repo/balancer_request.py`
**Implementation:** `src/infra/clients/balancer_request.py`

Отправляет запросы балансировки команд внешним сервисам (`mix_balance_service`, `tournament_balance_service`) через RabbitMQ publish. Не блокирующий — результаты приходят асинхронно в handler `mixer_service.balancer.result`.

## Custom Methods

### `request_mix_formation`

```python
async def request_mix_formation(task_id: UUID, draft_id: UUID, players: list[BalancerPlayer], settings: MixBalanceSettings) -> None
```

Публикует запрос в очередь `mix_balance_service.balance` с `correlation_id=task_id` и `reply_to=mixer_service.balancer.result`. Используется для балансировки команд в режиме MIX (произвольный состав).

**Параметры:**
- `task_id` — ID задачи, используется как correlation_id
- `draft_id` — ID драфта
- `players` — список игроков с ролями, рейтингами, приоритетами
- `settings` — настройки балансировки (min/max игроков в команде, конфигурация ролей)

### `request_tournament_formation`

```python
async def request_tournament_formation(task_id: UUID, draft_id: UUID, players: list[BalancerPlayer], settings: TournamentBalanceSettings) -> None
```

Публикует запрос в очередь `tournament_balance_service.balance` с теми же correlation_id и reply_to. Используется для турнирной балансировки (фиксированное количество команд и игроков).

**Параметры:**
- `task_id` — ID задачи
- `draft_id` — ID драфта
- `players` — список игроков
- `settings` — количество команд, игроков в команде, конфигурация и приоритеты ролей

## Related Models

- `BalancerPlayer` / `MixBalanceSettings` / `TournamentBalanceSettings` — `src/core/models/balancer.py`

## Used By

- `TeamFormationService` — публикация запроса балансировки при `run()`.
