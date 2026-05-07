# ТЗ Для Агента: Этап 11. MVP-Срез

## Цель
Собрать минимальный end-to-end MVP Event Service из уже реализованных этапов. Приоритетный MVP должен покрыть одиночные игры как повторяемые match cycles внутри активного события: создание события, регистрацию, обработку заявок, выборку игроков, автоматическое формирование команд, создание одиночных матчей, фиксацию результатов, явное завершение события и RPC handlers для Gateway.

## Общий Контекст
- Event Service работает как внутренний RPC-сервис за Gateway.
- Gateway отвечает за REST, пользовательскую аутентификацию, обращение в Server Service и передачу `AccessDataRequest`.
- Event Service не обращается в Server Service напрямую.
- Rating effective calculation и rating match processing опциональны и управляются настройками.
- Balancer services внешние: `mix_balance_service.balance` и `tournament_balance_service.balance`.
- Alembic не синхронизировать в рамках MVP-среза, если это не отдельная явно поставленная задача.
- MVP должен иметь single-game path как первый законченный пользовательский сценарий. Сложные турнирные сетки из этапа 8 и captain draft из этапа 9 можно включать только после готовности single-game MVP.

## MVP-1: Event И Registration
- Создание события.
- Сохранение `server_id`.
- Назначение создателя локальным organizer.
- Настройка заявок, ролей, интеграций и кастомных полей.
- Активация события.
- Открытие регистрации через настройки/окно, а не обязательный глобальный status `REGISTRATION`.
- Подача заявки или auto-join.
- Обработка заявок organizer-ом.
- Получение списка заявок и игроков.

## MVP-2: Selection И Team Formation
- Создание выборки игроков из approved/active players.
- Подготовка rating snapshot.
- Работа с `rating.effective.calculate` включенным и выключенным.
- Вызов внешнего балансировщика.
- Сохранение нескольких вариантов распределения.
- Выбор варианта organizer-ом.
- Материализация `Team` и `TeamPlayer`.

## MVP-3: Single Match Cycles
- Одиночные матчи как повторяемая минимальная структура `Bracket -> Stage -> StageGroup -> Match -> MatchSlot`.
- Создание fixed slots для команд конкретного матча.
- Создание score stubs.
- Возможность иметь несколько последовательных или параллельных матчей внутри active event.
- Защита игроков активного матча от повторного выбора, если параллельное участие запрещено.
- Отсутствие tournament-only logic в single-match path.

## MVP-4: Single Match Results И Event Completion
- Фиксация результата одиночного матча.
- Определение winner/loser/draw/forfeit.
- Формирование payload для `rating.match.process`.
- Публикация rating payload только при включенной интеграции.
- Освобождение/обновление статусов игроков после завершения матча.
- Явное завершение события отдельной командой organizer-а, только если нет активных матчей и блокирующих операций.

## MVP-5: RPC Handlers
- RPC handlers для Gateway по основным MVP-командам.
- DTO parsing и response DTO.
- Прокидывание `AccessDataRequest` в use cases.
- Healthcheck.
- Import/start без ссылок на `src.domain` и `src.infra.static`.

## Optional MVP Extension
- Если этап 8 уже реализован, MVP можно расширить single elimination tournament path.
- Если этап 9 уже реализован, MVP можно расширить captain draft team formation path.
- Double elimination, swiss, round robin и captain draft не должны блокировать single-game MVP.
- Если tournament/captain draft extension не готов, single-game MVP все равно считается валидным первым срезом.

## Access Model MVP
- Локальный organizer имеет полное управление своим мероприятием.
- `event_create` требуется только если создание мероприятий не открыто всем участникам пространства.
- `event_admin_*` permissions нужны для административного override над чужими мероприятиями.
- `server_ban` запрещает создание, вступление, заявки и organizer-действия.
- `mix_ban` запрещает участие в одиночном/mix event.
- `tournament_ban` запрещает участие в tournament event.

## Out Of Single-Game MVP
- Double elimination production polish.
- Swiss production polish.
- Round robin groups production polish.
- Captain draft.
- Выравнивание очередей tournament balancer, если внешний сервис еще не согласован.
- Расширенные метрики качества баланса.
- Повторные draft-циклы сверх минимального `allow_multiple_drafts`.
- Публичный REST внутри Event Service.

## End-To-End Сценарий Приемки
- Gateway payload содержит `AccessDataRequest` с `server_id`, `member_id`, permission/restriction masks.
- Пользователь создает event и становится organizer.
- Organizer настраивает регистрацию и активирует event.
- Участник подает заявку.
- Organizer принимает заявку.
- Event Service создает EventPlayer.
- Organizer создает выборку approved players.
- Event Service готовит rating snapshot.
- Event Service вызывает rating effective calculation, если включено, или использует open-rating snapshot, если выключено.
- Event Service вызывает balancer и сохраняет variants.
- Organizer выбирает variant.
- Event Service создает teams.
- Event Service создает одиночный match setup.
- Organizer фиксирует результат одиночного матча.
- Event Service формирует rating match payload.
- Event Service публикует rating match payload, если включено, или сохраняет локально, если выключено.
- Event Service освобождает/обновляет статусы игроков матча.
- Event остается active и может принять следующий match cycle.
- Organizer явно завершает event, когда активных матчей больше нет.
- Event Service возвращает итоговый результат/summary.

## Задачи
- Проверить, что результаты этапов 1-7 соединяются в единый single-game MVP flow.
- Если нужен full tournament MVP, отдельно проверить готовность этапа 8.
- Если нужен captain draft MVP extension, отдельно проверить готовность этапа 9.
- Добить missing DTO/use cases/handlers только для MVP path.
- Убрать или отложить не-MVP ветки, которые блокируют сборку.
- Обновить документацию RPC-команд под фактический MVP контракт.

## Не Делать
- Не блокировать single-game MVP сложными tournament formats или captain draft.
- Не делать optional rating integrations обязательными.
- Не добавлять прямой ServerClient в Event Service.
- Не синхронизировать Alembic без отдельной задачи.
- Не писать и не исправлять тесты в рамках MVP-среза; тестирование описано и выполняется в этапе 10.

## Критерии Приемки
- Single-game MVP happy path проходит через use cases или RPC handlers с fake clients.
- Один active event может провести минимум один match cycle и остаться готовым к следующему cycle.
- Event завершается только явной командой и только без активных матчей.
- Сервис импортируется и стартует локально.
- `uv run mypy src` проходит или оставшиеся ошибки явно задокументированы.
- Документация отражает фактические MVP-команды и ограничения.

## Команды Проверки
- `uv run mypy src`
