# Event Model Changelog

## Назначение
- Этот файл фиксирует все осознанные изменения ORM-моделей, DTO, enum-ов и repository contracts при реализации Event Service.
- Реализация должна идти по существующим моделям Event Service. Новые сущности и поля добавляются только если текущая модель не выражает обязательный сценарий этапа.
- Это не migration notes: Alembic и миграции остаются вне этих ТЗ.

## Правила Заполнения
- Добавлять запись в этом файле в том же изменении, где меняется ORM/DTO/enum/repository contract.
- Описывать минимальное изменение, а не общий план реализации.
- Указывать, почему нельзя было обойтись существующей моделью.
- Если этап не менял модельный контракт, добавить короткую запись `Без изменений модели`.

## Шаблон Записи
```md
## YYYY-MM-DD. Этап N. <краткое название>
- Статус: planned | implemented | changed | no model changes
- Затронутые сущности: `Event`, `Draft`, `Team`, ...
- Затронутые файлы: `src/core/models/...`, `src/infra/postgre/models/...`, `src/core/interfaces/repo/...`
- Изменение: <минимальное описание добавленных/измененных полей, DTO, enum values или repo methods>
- Причина: <какой обязательный сценарий нельзя было выразить существующей моделью>
- Почему минимально: <почему расширение существующей модели предпочтительнее новой сущности/параллельной схемы>
- Alembic: не изменялся
```

## Записи

## 2026-05-08. Удаление устаревшего registration_type
- Статус: changed
- Затронутые сущности: `Event`
- Затронутые файлы:
  - `src/core/models/event.py`, `src/core/commands/event.py`, `src/core/results/event.py` — удалены `RegistrationType` и поле `registration_type` из DTO/контрактов события
  - `src/infra/postgre/models/event.py` — удалена ORM-колонка `EventModel.registration_type`
  - `alembic/versions/4b4ab863dbce_.py` — начальная схема больше не создает колонку `registration_type`
  - `docs/*` — удалены упоминания `RegistrationType` и ошибочная трактовка отдельного типа регистрации
- Изменение: `registration_type` полностью удален из Event Service; сценарий заявка/auto-join остается выражен существующим `use_application`.
- Причина: поле изначально предназначалось для разделения командной и одиночной регистрации, но командная регистрация была исключена; поздняя трактовка как `FREE`/`APPLICATION`/`INVITE` дублировала `use_application` и не использовалась бизнес-логикой.
- Почему минимально: отдельная сущность или новое поле не нужны; текущий обязательный сценарий одиночной регистрации уже покрывает `use_application`.
- Alembic: изменена начальная миграция схемы

## 2026-05-08. Этап 7. Результаты одиночных матчей и завершение event
- Статус: implemented
- Затронутые сущности: `Match`, `MatchScore`, `Event`
- Затронутые файлы:
  - `src/core/models/match.py`, `src/infra/postgre/models/match.py` — добавлено `Match.result_snapshot: JSON | None` для локального payload/snapshot результата матча
  - `src/core/interfaces/repo/match.py`, `src/infra/postgre/repo/match.py` — добавлены `get_event_context(...)`, `list_by_event(...)`, update по `match_id`
  - `src/core/interfaces/repo/match_score.py`, `src/infra/postgre/repo/match_score.py` — update по `score_id` для фиксации счета без требования `id` в DTO
  - `src/core/commands/match.py`, `src/core/results/match.py` — расширены команды/result DTO для result recording, forfeit, match list/get и rating payload
  - `src/core/commands/event.py`, `src/core/usecases/event.py`, `src/core/usecases/match.py`, `src/infra/rabbit/api/event.py`, `src/infra/rabbit/api/match.py`, `src/dependency.py`, `src/env_config.py` — добавлены use cases/RPC для `event.match.result.record`, `event.match.get`, `event.match.list`, `event.complete` и настройка `RATING_MATCH_PROCESS_ENABLED`
- Изменение:
  1. Результат одиночного матча сохраняет счет в существующих `MatchScore`, завершает матч через `Match.time_end` и сохраняет JSON snapshot с winner/draw/forfeit/rating payload.
  2. `rating.match.process` публикуется только при включенном `RATING_MATCH_PROCESS_ENABLED`; при выключенной интеграции payload остается в `Match.result_snapshot`.
  3. Завершение event вынесено в отдельную команду `event.complete` и запрещено при наличии активных матчей.
- Причина: Stage 7 требует локально сохранять result snapshot и блокировать повторную фиксацию результата; существующих `MatchScore` и `time_end` было достаточно для счета/занятости, но не для rating payload и winner/forfeit metadata.
- Почему минимально: новая таблица не добавлялась; snapshot хранится в существующей сущности `Match`, а занятость игроков снимается уже существующим признаком `Match.time_end is not null`.
- Alembic: не изменялся

## 2026-05-08. Этап 6. Одиночные матчи и слоты
- Статус: implemented
- Затронутые сущности: `Stage`, `StageGroup`, `Team`, `Match`
- Затронутые файлы:
  - `src/core/models/stage.py` — добавлен `StageFormat.SINGLE_MATCH`
  - `src/infra/postgre/models/application_custom_field.py` — добавлена обратная relationship `filled_fields` для уже существующего `FilledApplicationField.custom_field`
  - `src/infra/postgre/models/stage_group.py` — добавлена обратная relationship `source_slots` для уже существующего `MatchSlot.source_group`
  - `src/infra/postgre/models/team.py` — добавлены обратные relationships `match_scores` для уже существующего `MatchScore.team` и `bracket_placements` для уже существующего `BracketPlacement.team`
  - `src/infra/postgre/models/match.py` — исправлены `foreign_keys` references с `MatchSlot.*` на существующий ORM class `MatchSlotModel.*`
  - `src/core/interfaces/repo/match.py`, `src/infra/postgre/repo/match.py` — добавлены методы `next_match_index(...)`, `list_active_team_ids_by_event(...)`, `list_active_draft_ids_by_event(...)`
  - `src/core/commands/match.py` — расширен `SetupMatchCommand` полями `draft_id` и `scheduled_at`
  - `src/core/results/match.py` — добавлены `SingleMatchView` и `SingleMatchSlotView`
  - `src/core/usecases/match.py`, `src/infra/rabbit/api/match.py`, `src/dependency.py` — добавлен use case/RPC/DI для `event.match.setup`
  - `src/core/usecases/draft.py` — занятость игроков для новых выборок теперь определяется через draft ids активных незавершенных матчей
- Изменение:
  1. Single-game контейнер создается как `Bracket -> Stage(SINGLE_MATCH) -> StageGroup` и переиспользуется для последующих одиночных матчей события.
  2. Новый матч получает fixed `MatchSlot` для каждой команды и `MatchScore` stub со счетом `0`, где `MatchScore.team_id` фиксирует команду слота.
  3. Проверка занятости использует активные незавершенные матчи (`Match.time_end is null`) и связанные через score stubs команды/draft ids.
- Причина: Stage 6 требует отличать одиночный match setup от tournament-only stage formats и проверять повторное использование команд/выборок через незавершенные матчи.
- Почему минимально: новые PostgreSQL-сущности и поля не добавлялись; связь матча с командами выражена существующими `MatchSlot` + `MatchScore.team_id`, а связь с выборкой выводится через `Team.draft_id`.
- Alembic: не изменялся

## 2026-05-08. Этапы 2-5. Доработка RPC/use case contracts
- Статус: changed
- Затронутые сущности: `Event`, `Application`, `Draft`, `TeamFormationJob`, `RatingSnapshotPlayer`
- Затронутые файлы:
  - `src/core/interfaces/repo/event.py`, `src/infra/postgre/repo/event.py` — добавлены `list_public_by_server(...)` и `list_by_server(...)`
  - `src/core/commands/application.py` — mutable defaults заменены на `Field(default_factory=...)`
  - `src/core/commands/draft.py` — добавлены параметры автоматической выборки `statuses`, `limit`, `pinned_only`
  - `src/core/commands/team_formation.py` — добавлен `RatingSnapshotInput`, `rating_snapshot`, `rating_settings`, `team_count`
  - `src/core/results/team_formation.py` — добавлен `calculated_rating`, mutable defaults заменены на `Field(default_factory=...)`
  - `src/core/usecases/_access.py` — добавлены helper-ы server context/admin permission/server ban
  - `src/core/usecases/event.py`, `organizer.py`, `application.py`, `player.py`, `draft.py`, `team.py`, `team_formation.py` — исправлена семантика access checks и stage 5 rating/balancer flow
  - `src/dependency.py`, `src/infra/rabbit/main.py` — добавлен локальный `db_session` context для rollback в exception middleware
- Изменение:
  1. Event listing теперь фильтруется по `server_id` на уровне repository до пагинации.
  2. Server-admin permissions применяются только в совпадающем `access_data.server_id` context; `server_ban` добавлен к organizer/admin write actions.
  3. Application role priorities нормализуются к `SelectedGameRole.id`, чтобы не писать внешний role id в FK `player_role_table.game_role_id`.
  4. Stage 5 принимает rating snapshot от Gateway, валидирует его по draft players/roles, сохраняет `open_rating`, `calculated_rating`, `effective_rating` и `rating_source`.
  5. Balancer request теперь передает calculated rating в `PlayerRole.rating`; tournament team count задается командой или выводится из числа игроков.
- Причина: review стадий 2-5 выявил, что access masks применялись без server context, stage 4 некорректно нормализовал role ids, а stage 5 не выполнял обязательный contract rating snapshot -> calculated rating -> balancer.
- Почему минимально: изменения ограничены существующими use cases/DTO/repository protocol без добавления нового service layer и без новых ORM/PostgreSQL сущностей.
- Alembic: не изменялся

## 2026-05-07. Этап 5. Выборка и формирование команд
- Статус: implemented
- Затронутые сущности: `Draft`, `TeamFormationVariant` (result/cache DTO, не ORM)
- Затронутые файлы:
  - `src/core/models/draft.py` — добавлено `id: UUID` в `DraftUpdate`
  - `src/core/interfaces/clients/rating.py`, `mix_balancer.py`, `tournament_balancer.py` — протоколы возвращают `list[dict]` вместо Protocol-типов
  - `src/core/results/team_formation.py` — расширены DTO результата: `RatingSnapshotPlayer`, `TeamFormationVariantTeam`, `TeamFormationVariantMetrics`, `TeamFormationJob`
  - `src/core/commands/team_formation.py` — добавлено `use_effective_rating: bool` в `RunTeamFormationCommand`
  - `src/env_config.py` — добавлено `team_formation_variants_ttl_seconds: int`
  - `src/infra/redis/engine.py` — новый файл: `RedisSessionManager` по паттерну Server Service
  - `src/infra/redis/team_formation.py` — новый файл: `TeamFormationVariantStore` с поддержкой `save`, `get`, `get_latest_by_draft`, `delete`
  - `src/infra/clients/rating.py` — новый файл: `RatingClient`
  - `src/infra/clients/mix_balancer.py` — новый файл: `MixBalancerClient`
  - `src/infra/clients/tournament_balancer.py` — новый файл: `TournamentBalancerClient`
  - `src/core/usecases/draft.py` — новый файл: `CreateDraftUseCase`, `GetDraftUseCase`, `ListDraftsUseCase`
  - `src/core/usecases/team_formation.py` — новый файл: `RunTeamFormationUseCase`, `GetTeamFormationUseCase`, `ChooseTeamFormationVariantUseCase`
  - `src/core/usecases/team.py` — новый файл: `ListTeamsUseCase`
  - `src/infra/rabbit/api/draft.py` — новый файл: 3 RPC handler
  - `src/infra/rabbit/api/team_formation.py` — новый файл: 3 RPC handler
  - `src/infra/rabbit/api/team.py` — новый файл: 1 RPC handler
  - `src/infra/rabbit/api/__init__.py` — подключены новые роутеры
  - `src/infra/rabbit/main.py` — добавлен `RedisSessionManager` в lifespan, `broker` в context
  - `src/dependency.py` — добавлены DI providers для Redis, clients, и 7 use cases
- Изменение:
  1. Добавлено `id: UUID` в `DraftUpdate` для корректной работы `BaseRepository.update` (merge).
  2. Добавлены result/cache DTO `TeamFormationVariant`, `TeamFormationJob`, `RatingSnapshotPlayer`, `TeamFormationVariantTeam`, `TeamFormationVariantMetrics` в `src/core/results/team_formation.py`.
  3. Добавлен `TeamFormationVariantStore` в `src/infra/redis/team_formation.py` для временного хранения вариантов балансировки в Redis.
  4. Добавлен `RedisSessionManager` в `src/infra/redis/engine.py` по паттерну Server Service.
  5. Добавлены три RPC-клиента: `RatingClient`, `MixBalancerClient`, `TournamentBalancerClient` в `src/infra/clients/`.
  6. Реализованы use cases создания выборки (`CreateDraftUseCase`), запуска формирования команд (`RunTeamFormationUseCase`), получения job (`GetTeamFormationUseCase`), выбора варианта (`ChooseTeamFormationVariantUseCase`), получения команд (`ListTeamsUseCase`).
  7. Добавлены RPC handlers: `event.draft.create`, `event.draft.get`, `event.draft.list`, `event.team_formation.run`, `event.team_formation.get`, `event.team_formation.choose`, `event.team.list`.
- Причина: Stage 5 требует реализации выборки игроков, интеграции с внешними балансировщиками, временного хранения вариантов в Redis и выбора варианта организатором. Необходимы новые DTO, Redis-инфраструктура, RPC-клиенты и use cases.
- Почему минимально: Варианты балансировки хранятся только в Redis (нет новых ORM/PostgreSQL таблиц). `DraftUpdate` расширен полем `id` по аналогии с `ApplicationUpdate`. Все остальные изменения — новые файлы (usecases, handlers, clients, store).
- Alembic: не изменялся

## 2026-05-07. Этап 4.5. Фикс Permissions И Restrictions
- Статус: implemented
- Затронутые сущности: —
- Затронутые файлы:
  - `src/core/usecases/_access.py` — переписан: заменены ручные ошибочные биты на `PermissionCode`/`RestrictionCode` enum enums по canonical Server Service enum order
  - `docs/EVENT_MODEL_CHANGELOG.md` — обновлён статус
- Изменение:
  1. Добавлены `PermissionCode` (IntEnum, 32 members) и `RestrictionCode` (IntEnum, 4 members), зеркалирующие Server Service `PERMISSION` и `RESTRICTION`.
  2. `P_EVENT_CREATE` исправлен с `1 << 5` на `1 << 24`; все event permission bits теперь `1 << 24`..`1 << 31`.
  3. `R_SERVER_BAN` = `1 << 0`, `R_MIX_BAN` = `1 << 1`, `R_TOURNAMENT_BAN` = `1 << 2` остались без изменений (уже были корректны).
  4. Добавлен `R_SELF_EDIT_NAME` = `1 << 3` (ранее отсутствовал).
  5. Остальные event admin permission bits исправлены: `P_EVENT_ADMIN_VIEW` с `1 << 6` на `1 << 25`, `P_EVENT_ADMIN_UPDATE` с `1 << 7` на `1 << 26`, `P_EVENT_ADMIN_MANAGE_ORGANIZERS` с `1 << 8` на `1 << 27`, `P_EVENT_ADMIN_MANAGE_PLAYERS` с `1 << 9` на `1 << 28`, `P_EVENT_ADMIN_MANAGE_BRACKET` с `1 << 10` на `1 << 29`, `P_EVENT_ADMIN_CANCEL` с `1 << 11` на `1 << 30`, `P_EVENT_ADMIN_COMPLETE` с `1 << 12` на `1 << 31`.
  6. Use cases (`event.py`, `organizer.py`, `application.py`, `player.py`) не требуют изменений импортов — все именованные константы сохранены.
- Причина: этапы 1-4 уже реализованы, но текущие access helpers использовали ошибочные bit positions (`1 << 5`..`1 << 12`) вместо canonical Server Service `PERMISSION` enum order (`1 << 24`..`1 << 31`).
- Почему минимально: изменение затрагивает только `_access.py` — не требует ORM/DTO/schema изменений, не меняет сигнатуры use cases.
- Alembic: не изменялся

## 2026-05-07. Этап 5. Redis Для Вариантов Балансировки
- Статус: planned
- Затронутые сущности: `TeamFormationVariant`, `Draft`, `Team`, `TeamPlayer`
- Затронутые файлы: `docs/EVENT_STAGE_05_SELECTION_TEAM_FORMATION_TZ.md`, `docs/EVENT_MODULE_IMPLEMENTATION_PLAN.md`, `docs/EVENT_AGENT_IMPLEMENTATION_CONTEXT.md`, `docs/EVENT_STAGE_01_DATABASE_STABILIZATION_TZ.md`, `docs/EVENT_STAGE_10_TESTING_TZ.md`, `docs/EVENT_STAGE_11_MVP_SLICE_TZ.md`
- Изменение: зафиксировано, что варианты балансировки не являются PostgreSQL/ORM сущностями. `TeamFormationVariant` используется как result/cache DTO, variants и metrics временно хранятся в Redis с TTL до выбора organizer-ом.
- Redis-паттерн: использовать подход из `mixtura-backend-server` (`RedisSessionManager`, FastStream context `redis_engine`, DI `get_redis_session`), но вместо server-specific cookie repository сделать `TeamFormationVariantStore`.
- Причина: варианты балансировки являются промежуточным результатом внешнего balancer и нужны только до выбора одного варианта; долговечно сохраняются только итоговые `Team`/`TeamPlayer`.
- Почему минимально: Redis-хранилище позволяет не добавлять таблицы `team_formation_variant`/`team_formation_variant_player` и не расширять существующую PostgreSQL-схему ради временных данных.
- Alembic: не изменялся

## 2026-05-07. Этап 4. Заявки и участники
- Статус: implemented
- Затронутые сущности: `Application`, `EventPlayer`, `PlayerRole`
- Затронутые файлы:
  - `src/core/models/application.py` — добавлено `role_priorities: dict[str, int]` в `Application`, `ApplicationCreate`, `ApplicationUpdate`; добавлено `id: UUID` в `ApplicationUpdate`
  - `src/infra/postgre/models/application.py` — добавлена колонка `role_priorities: JSON`
  - `src/core/interfaces/repo/application.py` — добавлен `status: ApplicationStatus | None` в `list_by_event`; изменён `update(self, dto)` → `update(self, application_id: UUID, dto)`
  - `src/core/interfaces/repo/player.py` — добавлен `status: EventPlayerStatus | None` в `list_by_event`; изменён `update(self, dto)` → `update(self, player_id: UUID, dto)`
  - `src/infra/postgre/repo/application.py` — переопределён `update` для работы с `application_id`; добавлена фильтрация по `status` в `list_by_event`
  - `src/infra/postgre/repo/player.py` — переопределён `update` для работы с `player_id`; добавлена фильтрация по `status` в `list_by_event`
  - `src/core/usecases/application.py` — новый файл: 4 use case (SubmitApplicationUseCase, ReviewApplicationUseCase, GetApplicationUseCase, ListApplicationsUseCase)
  - `src/core/usecases/player.py` — новый файл: 3 use case (ListPlayersUseCase, UpdatePlayerStatusUseCase, RemovePlayerUseCase)
  - `src/infra/rabbit/api/application.py` — новый файл: 4 RPC handler
  - `src/infra/rabbit/api/player.py` — новый файл: 3 RPC handler
  - `src/infra/rabbit/api/__init__.py` — подключены новые роутеры
  - `src/dependency.py` — добавлены 7 use case providers
- Изменение:
  1. Добавлено поле `role_priorities: dict[str, int]` в DTO и ORM Application для хранения приоритетов ролей, выбранных участником при подаче заявки (JSON колонка, т.к. вариант с новой сущностью был бы избыточен).
  2. Добавлено `id: UUID` в `ApplicationUpdate`, чтобы базовый `BaseRepository.update` (merge) мог корректно идентифицировать запись.
  3. `ApplicationRepositoryProtocol.update` и `PlayerRepositoryProtocol.update` изменены с `(dto)` на `(entity_id: UUID, dto)` по аналогии с `EventRepository`, чтобы не требовать `id` в Update DTO.
  4. В `list_by_event` обоих репозиториев добавлен опциональный фильтр по `status`.
  5. Реализованы use cases и RPC handlers для полного цикла: подача заявки → обработка (approve/reject/waitlist) → создание EventPlayer + PlayerRole.
- Причина: Stage 4 требует реализации join/application flow и управления участниками. Существующая модель Application не хранила role_priorities, а репозитории не поддерживали фильтрацию по статусу и корректный update по идентификатору.
- Почему минимально: `role_priorities` добавлено как JSON колонка в существующую Application, а не создана новая сущность. Остальные изменения — методы репозиториев и новый слой use cases/RPC.
- Alembic: не изменялся

## 2026-05-07. Этап 1. Стабилизация базы
- Статус: implemented
- Затронутые сущности: все 24 entity (Event, Organizer, Application, ApplicationCustomField, ApplicationIntegration, ApplicationTimeSettings, Bracket, BracketPlacement, Draft, DraftedPlayer, EventPlayer, FilledApplicationField, Match, MatchScore, MatchSlot, PlayerRole, RequiredIntegration, RoundRobinSettings, SelectedGameRole, Stage, StageGroup, SwissSettings, Team, TeamPlayer)
- Затронутые файлы:
  - `src/core/models/*.py` — все 24 файла DTO
  - `src/infra/postgre/models/event.py`, `event_player.py`, `stage.py`
  - `src/core/interfaces/repo/*.py` — все 24 протокола
  - `src/infra/postgre/repo/base.py`, `src/infra/postgre/repo/*.py` — все 24 репозитория
  - `src/core/service/` — удалён устаревший слой
- Изменение:
  1. Удалён `src/core/service/*.py` (stale-слой с `src.domain.*` импортами и unsuffixed ORM импортами).
  2. Добавлены enum-ы: `EventMatchType`, `StageFormat`, `EventPlayerStatus`.
  3. Добавлено поле `server_id: UUID` в `Event`/`EventModel`.
  4. Добавлено поле `status: EventPlayerStatus` в `EventPlayer`/`EventPlayerModel`.
  5. `match_type: str` → `match_type: EventMatchType` (DTO и ORM).
  6. `format: str` → `format: StageFormat` в `Stage`/`StageModel` (DTO и ORM).
  7. Все 24 DTO разделены на `*Create`/`*Read` (существующий unsuffixed класс как Read) / опциональный `*Update`.
  8. `BaseRepository` расширен с `Generic[ModelType, DTOType]` до `Generic[ModelType, CreateDTO, ReadDTO, UpdateDTO]`.
  9. Все 24 репозитория и протокола обновлены: `create(dto: *Create) -> *Read`, `update(dto: *Update) -> *Read`.
- Причина: Stage 1 требует стабилизации базы: устранение stale-зависимостей, приведение DTO к `*Create`/`*Read`/`*Update` контракту, синхронизация ORM и DTO.
- Почему минимально: все изменения выполнены на существующих моделях без создания параллельных схем. Enum-ы добавлены только для полей, уже существующих как `str`.
- Alembic: не изменялся

## 2026-05-07. Документация. Базовое правило
- Статус: planned
- Затронутые сущности: все Event Service model contracts
- Затронутые файлы: `docs/EVENT_MODULE_IMPLEMENTATION_PLAN.md`, `docs/EVENT_STAGE_01_DATABASE_STABILIZATION_TZ.md`, `docs/EVENT_MODEL_CHANGELOG.md`
- Изменение: зафиксировано правило реализации по существующим моделям с минимальными документируемыми изменениями.
- Причина: следующим этапам нужен единый источник информации о том, где и почему модельный контракт был расширен.
- Почему минимально: отдельный changelog не требует менять код, Alembic или структуру этапов.
- Alembic: не изменялся

## 2026-05-07. Этап 2. Внешние контракты модуля
- Статус: implemented
- Затронутые сущности: — (не затрагивались)
- Затронутые файлы: `src/core/commands/*`, `src/core/results/*`, `src/core/interfaces/clients/*`, `src/core/response.py`, `src/infra/rabbit/*`, `src/dependency.py`, `start.py`, `entrypoint.sh`
- Изменение: созданы command DTO (14 файлов), result DTO (3 файла), client protocols (3 файла), response envelope, FastStream app, агрегирующий RabbitRouter, healthcheck handler, dependency module с 24 providers для репозиториев, исправлены entrypoint и docker entrypoint.
- Причина: этап 2 не затрагивает ORM/DTO/enum/repository contract, а реализует внешний RPC-контур модуля.
- Почему минимально: новая функциональность (commands, results, clients, rabbit infra) не требует изменения существующих моделей. Все изменения — добавление слоя над стабильной моделью.
- Alembic: не изменялся

## 2026-05-07. Этап 3. Управление мероприятиями
- Статус: implemented
- Затронутые сущности: `Event`, `Organizer`
- Затронутые файлы:
  - `src/core/interfaces/repo/event.py` — изменён `update(self, dto: EventUpdate)` → `update(self, event_id: UUID, dto: EventUpdate)`, добавлен `transition_status(self, event_id: UUID, new_status: EventStatus)`
  - `src/infra/postgre/repo/event.py` — переопределён `update` для работы без `id` в `EventUpdate`, реализован `transition_status`
  - `src/core/usecases/_access.py` — новый файл с константами restriction/permission bitmask и хелперами
  - `src/core/usecases/event.py` — новый файл: 9 use cases для управления мероприятиями
  - `src/core/usecases/organizer.py` — новый файл: 3 use cases для управления организаторами
  - `src/infra/rabbit/api/event.py` — новый файл: 9 RPC handlers для event-команд
  - `src/infra/rabbit/api/organizer.py` — новый файл: 3 RPC handlers для organizer-команд
  - `src/infra/rabbit/api/__init__.py` — подключены новые роутеры
  - `src/dependency.py` — добавлены 12 use case providers
- Изменение:
  1. `EventRepositoryProtocol.update` изменён с `(dto: EventUpdate)` на `(event_id: UUID, dto: EventUpdate)`, т.к. `EventUpdate` не содержит `id` и базовый `BaseRepository.update` не может корректно идентифицировать запись через merge.
  2. Добавлен `EventRepositoryProtocol.transition_status(event_id, new_status)` для выполнения статусных переходов с валидацией через `EventModel.transition_to()`.
  3. Реализованы use cases: `CreateEventUseCase`, `GetEventUseCase`, `ListPublicEventsUseCase`, `ListPrivateEventsUseCase`, `UpdateEventUseCase`, `ActivateEventUseCase`, `OpenRegistrationUseCase`, `CloseRegistrationUseCase`, `CancelEventUseCase`.
  4. Реализованы use cases: `ListOrganizersUseCase`, `AddOrganizerUseCase`, `RemoveOrganizerUseCase`.
  5. Все use cases проверяют `access_data` (restriction_mask и permission_mask) в соответствии с контрактом `SERVER_GATEWAY_EVENT_INTEGRATION.md`.
  6. Все 12 use cases подключены к FastStream RPC handlers через dependency injection.
- Причина: Stage 3 требует реализации сценариев создания, чтения, настройки, публикации/активации, открытия/закрытия регистрации, отмены события и управления организаторами. Для этого нужен слой use cases, handler-ы и dependency wiring.
- Почему минимально: изменение repository protocol минимально — только `update` signature и добавление `transition_status`. Новые файлы — инфраструктура (use cases, handlers), а не изменения существующей модели. ORM/DTO/enum не менялись (кроме addition методов в репозитории).
- Alembic: не изменялся
