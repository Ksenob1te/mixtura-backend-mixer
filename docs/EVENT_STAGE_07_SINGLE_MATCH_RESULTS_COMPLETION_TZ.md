# ТЗ Для Агента: Этап 7. Одиночные Игры: Результаты И Завершение

## Цель
Реализовать фиксацию результатов одиночных матчей и явное завершение активного события. После этапа Event Service должен уметь завершать отдельные single-game matches без автоматического завершения всего event.

## Общий Контекст
- Этот этап продолжает этап 6 и работает только с одиночными матчами, не со сложными tournament brackets.
- Сложные турнирные сетки, продвижение по bracket routes, standings и `advance_count` будут реализованы позже в этапе 8.
- Event Service фиксирует счет команд, победителя/ничью, техническое поражение и match result. Итоговые места относятся к турнирам; для серии одиночных игр формируется summary/statistics события, если это задано бизнес-правилами.
- Завершение одного матча не завершает event автоматически: активное событие может продолжать принимать игроков, формировать новые выборки и запускать новые матчи.
- Расчет рейтинга выполняется внешним Rating Service через опциональный `rating.match.process`.
- Если `rating.match.process` выключен, Event Service сохраняет локальный payload/snapshot без публикации.
- Organizer имеет полную власть над своим мероприятием.
- Server-admin override `event_admin_manage_bracket` и `event_admin_complete` может использоваться для административного вмешательства.

## RecordSingleMatchResultUseCase
- Проверить доступ: organizer или server-admin override.
- Проверить, что match существует и принадлежит event/server из `access_data`.
- Проверить, что match является одиночным матчем, а не tournament bracket match.
- Проверить, что match находится в состоянии, допускающем фиксацию результата.
- Проверить, что все required slots заполнены командами.
- Зафиксировать счет команд.
- Определить winner, loser или draw.
- Поддержать technical loss/forfeit.
- Заблокировать повторную фиксацию результата без отдельного rollback/override flow.
- Создать payload для rating updates.
- Сохранить локальный match result snapshot.
- Завершить матч так, чтобы связанная с ним выборка перестала считаться активной занятостью игроков для новых выборок.

## Rating Match Payload
```python
MatchResult(
    match_id=UUID,
    match_time=datetime,
    teams=[MatchTeam(team_id=UUID, player_ids=[UUID])],
    team_ranks=[1.0, 2.0],
    players=[MatchPlayer(member_id=UUID, role_id=UUID, open_rating=float)],
    settings=RatingSettings(...),
)
```

## Rating Rules
- `team_ranks` использует порядок мест, где `1.0` означает первое место.
- Для winner/loser в двухкомандном матче использовать `[1.0, 2.0]`.
- Для ничьи использовать равные ranks, если OpenSkill flow это поддерживает.
- `players` должен содержать всех members из `teams[*].player_ids`.
- `open_rating` должен быть snapshot на момент матча, а не текущее произвольное значение.
- Публиковать `rating.match.process` только если интеграция включена.

## CompleteSingleGameEventUseCase
- Выполняется отдельной organizer/admin командой, а не автоматически после каждого матча.
- Проверить, что в event нет активных матчей.
- Проверить, что нет незавершенных обязательных операций, которые должны блокировать завершение event.
- Зафиксировать итоговые данные/summary для события. Для серии одиночных игр итоговые места могут отсутствовать или строиться отдельной статистикой, если это задано бизнес-правилами.
- Убедиться, что rating payload либо опубликован, либо сохранен локально при выключенной интеграции.
- Перевести event в `COMPLETED` по правилам `event_flow.ini`.
- Вернуть итоговый result DTO для Gateway.

## Rollback И Override
- По умолчанию повторная фиксация результата запрещена.
- Если нужен rollback/override, его нужно проектировать отдельным command/use case с явной проверкой organizer или server-admin override.
- Не пытаться незаметно пересчитать rating updates при изменении результата; это отдельный контракт с Rating Service.

## RPC
- `event.match.result.record`: зафиксировать результат одиночного матча.
- `event.match.get`: получить матч, slots, scores и result snapshot.
- `event.match.list`: получить матчи события с фильтрами по статусу.
- `event.complete`: явно завершить событие, если нет active matches и блокирующих операций.
- `event.match.result.rollback`: не реализовывать по умолчанию; оставить как отдельный будущий admin/override flow, если потребуется.

## Задачи
- Реализовать `RecordSingleMatchResultUseCase`.
- Реализовать winner/draw/forfeit detection для одиночной игры.
- Реализовать локальное сохранение match result snapshot.
- Реализовать снятие занятости игроков через завершение матча и деактивацию/закрытие связанной выборки.
- Реализовать optional publish в `rating.match.process`.
- Реализовать `CompleteSingleGameEventUseCase`.
- Подключить use cases к RPC handlers.

## Не Делать
- Не реализовывать продвижение по `single_elimination`/`double_elimination` routes.
- Не реализовывать standings для `round_robin` или `swiss`.
- Не реализовывать `advance_count`.
- Не делать `rating.match.process` обязательным.
- Не обращаться напрямую в Rating DB.
- Не менять уже завершенный матч без отдельного rollback/override flow.
- Не синхронизировать Alembic.
- Не писать и не исправлять тесты; тестирование вынесено в этап 10.

## Критерии Приемки
- Можно зафиксировать результат одиночного матча.
- Winner/loser/draw/forfeit определяются корректно для одиночной игры.
- Завершение одного матча не завершает event автоматически.
- Игроки завершенного матча перестают считаться занятыми через связанную выборку и могут попадать в новые выборки.
- Event переводится в `COMPLETED` только отдельной командой завершения и только если нет активных матчей.
- Rating payload публикуется только при включенной интеграции, иначе сохраняется локально.

## Команды Проверки
- `uv run mypy src`
