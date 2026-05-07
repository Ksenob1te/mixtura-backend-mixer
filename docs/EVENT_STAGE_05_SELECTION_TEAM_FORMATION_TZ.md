# ТЗ Для Агента: Этап 5. Выборка И Формирование Команд

## Цель
Реализовать выборку игроков, подготовку rating snapshot, интеграцию с внешними балансировщиками, сохранение вариантов команд и выбор варианта organizer-ом. После этапа из утвержденных игроков можно получить несколько вариантов команд и зафиксировать выбранный вариант.

## Общий Контекст
- `Draft` в текущем коде означает выборку игроков для конкретного цикла формирования команд, а не только капитанский драфт.
- Событие может поддерживать повторные выборки при `allow_multiple_drafts`.
- Выборки и team formation jobs имеют собственные статусы и не переводят весь event в глобальное состояние `FORMATION`.
- Балансировщики являются внешними сервисами. Event Service не реализует собственный C++/алгоритмический балансировщик.
- Rating Service опционален. `rating.effective.calculate` включается настройкой.
- Если effective rating выключен, open-rating snapshot используется как расчетный рейтинг и источник сохраняется явно.
- Organizer имеет полную власть над своим мероприятием и может запускать формирование команд без server permissions.
- Подроли не поддерживать в текущем срезе. Хотя tournament balancer умеет `subrole_ids`/`subroles`, Server Service пока не готов отдавать подроли в role set, поэтому Event Service не должен принимать, хранить, валидировать или отправлять подроли в balancer request.

## Rating Snapshot
- Собрать open/custom ratings игроков по ролям из payload, переданного Gateway, или из локального event override snapshot.
- Если `rating.effective.calculate` включен, отправить snapshot в Rating Service и получить `effective_rating` по каждой паре `member_id + role_id`.
- Если `rating.effective.calculate` выключен, использовать open-rating как calculated rating.
- Сохранить open rating, calculated rating, optional effective/hidden rating, источник расчета и время расчета.
- В балансировщики передавать calculated rating, приведенный к `int`, в `PlayerRole.rating`.

## Rating Service Contract
```python
EffectiveRatingRequest(
    draft_id=UUID,
    players=[Player(member_id=UUID, roles={role_id: PlayerRole(priority=int, open_rating=int)})],
    settings=RatingSettings(...),
)
```

```python
EffectiveRatingResponse(
    draft_id=UUID,
    players=[PlayerEffectiveRating(member_id=UUID, role_id=UUID, open_rating=float, effective_rating=float, hidden_rating=float)],
    created_at=datetime,
)
```

## Mix Balance Contract
- Queue: `mix_balance_service.balance`.
- Использовать для одиночного матча или двух команд.
- `len(players)` не больше `max_in_team * 2`.
- Все role ids должны существовать в `balance_settings.roles`.
- `min_in_team <= max_in_team`.
- Сумма role minimums не должна превышать `max_in_team`.
- Priority semantics: lower priority value is better preference. Нормализовать перед отправкой.

## Tournament Balance Contract
- Queue: `tournament_balance_service.balance`.
- Progress queue: `mix_balance_service.balance.progress`.
- Использовать для турнирного формирования нескольких команд.
- `len(players)` должен делиться на `players_in_team`.
- Сумма `RoleSettings.count_in_team` должна равняться `players_in_team`.
- Player role priority должен быть `>= 1` и `<= priority.max_priority`.
- Tournament service трактует higher priority value как higher preference. Нормализовать отдельно от mix balancer.
- Не заполнять `PlayerRole.subrole_ids` и `RoleSettings.subroles` в request. Подроли исключены из ТЗ до готовности Server Service.

## Основные Use Cases
- `CreateDraftUseCase`: создать выборку игроков вручную или автоматически по лимиту, статусам, pinned-флагу и ограничениям. Занятость игрока определять через наличие игрока в активной выборке, которая уже связана с незавершенным матчем; таких игроков исключать из новых выборок, если параллельное участие запрещено.
- `RunTeamFormationUseCase`: подготовить rating snapshot, выбрать balancer, отправить задачу, сохранить варианты распределения.
- `ChooseTeamFormationVariantUseCase`: выбрать вариант organizer-ом и материализовать команды в `Team`/`TeamPlayer`.
- Для ручного формирования команд rating snapshot должен приходить с клиента/Gateway payload вместе с выбранными игроками/ролями; Event Service валидирует и сохраняет snapshot, но не обращается за ним в Server Service.

## Сохранение Вариантов
- Хранить job формирования команд.
- Хранить несколько variants с quality metrics.
- Хранить players внутри variant: `member_id`, `event_player_id`, `team_id`, `game_role_id`, priority, calculated rating, rating source.
- Хранить метрики: разница силы команд, ролевое соответствие, разброс рейтингов, нарушения ограничений и raw metrics балансировщика.
- Материализация выбранного варианта создает `Team` и `TeamPlayer`.

## RPC
- `event.draft.create`: создать выборку игроков.
- `event.draft.get`: получить выборку с игроками и статусом.
- `event.draft.list`: получить выборки события.
- `event.team_formation.run`: запустить подготовку rating snapshot и внешний balancer.
- `event.team_formation.get`: получить job формирования команд и сохраненные variants.
- `event.team_formation.choose`: выбрать variant и материализовать команды.
- `event.team.list`: получить команды события после materialization.

## Задачи
- Добавить или привести DTO/results для `TeamFormationVariant`, rating snapshot и balancer results.
- Реализовать interfaces/clients для `RatingClient`, `MixBalancerClient`, `TournamentBalancerClient`.
- Реализовать `CreateDraftUseCase`.
- Реализовать подготовку rating snapshot с optional effective rating.
- Реализовать выбор balancer по типу события и количеству команд.
- Реализовать сохранение variants и materialization выбранного варианта.
- Подключить use cases к RPC handlers.

## Не Делать
- Не реализовывать собственный балансировщик внутри Event Service.
- Не делать `rating.effective.calculate` обязательным.
- Не обращаться напрямую в Rating DB или Server DB.
- Не реализовывать подроли и не прокидывать их во внешний балансировщик.
- Не реализовывать captain draft; он вынесен в этап 9 после сложных сеток.
- Не синхронизировать Alembic.
- Не писать и не исправлять тесты; тестирование вынесено в этап 10.

## Критерии Приемки
- Из approved/active event players можно создать выборку.
- Можно запустить team formation с включенным и выключенным `rating.effective.calculate`.
- В balancer request уходит calculated rating, а не произвольная текущая оценка.
- Игроки из активных выборок, уже связанных с незавершенными матчами, не попадают в новую выборку, если параллельное участие запрещено.
- Возвращенные варианты сохраняются с метриками.
- Organizer может выбрать вариант и получить созданные `Team`/`TeamPlayer`.

## Команды Проверки
- `uv run mypy src`
