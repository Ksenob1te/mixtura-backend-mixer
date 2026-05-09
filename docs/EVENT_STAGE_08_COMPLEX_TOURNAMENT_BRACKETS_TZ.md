# ТЗ Для Агента: Этап 8. Сложные Турнирные Сетки

## Цель
Реализовать сложные tournament bracket algorithms после того, как одиночные игры уже поддержаны этапами 6-7. После этапа Event Service должен уметь создавать и проводить турнирные структуры `single_elimination`, `double_elimination`, `round_robin`, `swiss` с продвижением участников, standings и итоговой таблицей.

## Общий Контекст
- Этот этап не нужен для минимальной поддержки одиночных игр.
- Этап опирается на базовые сущности match/stage/group/slot/result, реализованные для одиночного матча.
- Турнирные форматы являются расширением над match result primitives из этапа 7.
- Organizer имеет полную власть над своим мероприятием.
- Server-admin override `event_admin_manage_bracket`, `event_admin_cancel`, `event_admin_complete` может использоваться для административного вмешательства.

## Основные Сущности
- `Bracket`: контейнер сетки мероприятия.
- `Stage`: стадия турнира с форматом и порядком.
- `StageGroup`: группа внутри стадии.
- `BracketPlacement`: seed/позиция участника в сетке или группе.
- `Match`: матч внутри группы/стадии.
- `MatchSlot`: слот участника матча, может ссылаться на seed, team или результат предыдущего матча.
- `MatchScore`: счет матча.
- `MatchSlotSourceType`: источник слота, например fixed team, winner of match, loser of match, BYE.

## Поддерживаемые Форматы
- `single_elimination`: дерево победителей, BYE для неполной степени двойки.
- `double_elimination`: верхняя и нижняя сетки, маршруты победителей и проигравших.
- `round_robin`: все пары внутри группы, `meetings_per_pair` повторяет встречи.
- `swiss`: генерация следующего раунда по текущим очкам без повторных пар.

## GenerateTournamentBracketUseCase
- Проверить доступ: organizer или `event_admin_manage_bracket`.
- Проверить, что event принадлежит `access_data.server_id`.
- Проверить, что event является tournament event, а не одиночной игрой.
- Проверить, что команды или участники готовы к seed.
- Создать `Bracket` для события, если его еще нет.
- Создать стадии и группы с настройками формата.
- Создать `BracketPlacement` с учетом seed order и рейтингов команд, если они есть.
- Создать `Match` и `MatchSlot` structures.
- Создать `MatchScore` stubs, если модель предполагает отдельные строки score до фиксации результата.
- Вернуть `BracketView` или совместимый result DTO.

## Single Elimination
- Рассчитать ближайшую степень двойки для bracket size.
- Добавить BYE slots для недостающих участников.
- Создать первый раунд с seed placements.
- Создать последующие матчи с slots от winner предыдущих матчей.
- BYE должен автоматически продвигать участника или маркироваться так, чтобы result flow мог продвинуть его без ручного счета.
- Winner финала получает первое место, loser финала второе; остальные placement rules определить явно.

## Double Elimination
- Создать winners bracket.
- Создать losers bracket.
- Для каждого матча winners bracket определить маршрут winner дальше по winners path и loser в losers bracket.
- Для matches losers bracket определить winner path дальше по lower bracket.
- Финальный матч должен учитывать победителя upper и lower bracket.
- Если true double final нужен вторым матчем, явно зафиксировать это настройкой.

## Round Robin
- Для каждой группы создать пары всех участников.
- Учитывать `meetings_per_pair`.
- Распределить rounds так, чтобы участник не играл два матча в одном round, если это ограничение требуется.
- Считать standings: очки, wins/losses/draws, score diff и tie-breakers, если они заданы настройками.
- Поддержать `advance_count` для перевода лучших участников в следующую стадию.

## Swiss
- Генерировать первый round по seed или случайному распределению.
- Последующие rounds должны учитывать текущие очки и запрет повторных пар.
- Хранить историю пар.
- Считать standings: текущие очки, wins/losses/draws и tie-breakers.
- Поддержать генерацию следующего round после завершения текущего.
- Поддержать `advance_count` для перевода лучших участников в следующую стадию.

## Tournament Result Flow
- Переиспользовать winner/draw/forfeit detection из этапа 7.
- После фиксации результата tournament match выполнить bracket advancement или standings update.
- Для `single_elimination` winner продвигается в следующий winner slot, loser получает eliminated/final placement.
- Для `double_elimination` winner идет по upper/lower winner path, loser из upper bracket попадает в lower bracket, loser из lower bracket выбывает.
- Для `round_robin` и `swiss` обновляются standings без bracket-slot advancement.
- Ошибки маршрутизации должны быть атомарными: не фиксировать результат без корректного продвижения, если продвижение обязательно.

## CompleteTournamentEventUseCase
- Проверить, что все обязательные матчи завершены или имеют технический результат.
- Проверить, что все обязательные стадии завершены.
- Перевести участников между стадиями через `advance_count`.
- Зафиксировать итоговые места.
- Убедиться, что rating payload для завершенных матчей либо опубликован, либо сохранен локально при выключенной интеграции.
- Перевести event в `COMPLETED` по правилам `event_flow.ini`.

## RPC
- `event.tournament.bracket.generate`: создать tournament bracket/stages/groups/matches.
- `event.tournament.bracket.get`: получить `BracketView`.
- `event.tournament.standings.get`: получить standings для round robin/swiss или итоговую таблицу стадии.
- `event.tournament.round.generate`: сгенерировать следующий swiss round или следующий управляемый round, если формат требует ручного запуска.
- `event.match.result.record`: переиспользовать общий handler фиксации результата; внутри use case route должен учитывать, что match принадлежит tournament bracket.
- `event.tournament.stage.complete`: завершить стадию и выполнить `advance_count`.
- `event.tournament.complete`: завершить tournament event с итоговыми местами.

## Задачи
- Реализовать `GenerateTournamentBracketUseCase`.
- Реализовать генераторы матчей для `single_elimination`, `double_elimination`, `round_robin`, `swiss`.
- Реализовать seed participants в `BracketPlacement`.
- Реализовать tournament advancement после результата матча.
- Реализовать standings для `round_robin` и `swiss`.
- Реализовать завершение стадии и перевод участников через `advance_count`.
- Реализовать `CompleteTournamentEventUseCase`.
- Добавить result DTO для `BracketView`/`StandingsView`, если они нужны RPC responses.
- Подключить use cases к RPC handlers.

## Не Делать
- Не изменять single-match flow этапов 6-7 без необходимости.
- Не делать `rating.match.process` обязательным.
- Не обращаться напрямую в Rating DB.
- Не синхронизировать Alembic.
- Не писать и не исправлять тесты; тестирование вынесено в этап 10.

## Критерии Приемки
- Для `single_elimination` создается валидное дерево с BYE и продвижением победителей.
- Для `double_elimination` создаются winners/losers paths и корректная маршрутизация проигравших.
- Для `round_robin` создаются все пары и обновляется standings.
- Для `swiss` создаются rounds без повторных пар и обновляется standings.
- Стадия завершается только после обязательных матчей.
- Tournament event завершается с итоговой таблицей.

## Команды Проверки
- `uv run mypy src`
