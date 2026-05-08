# Event Agent Implementation Context

Используй этот файл как общий контекст для агента, который реализует конкретный этап Event Service.

Перед запуском агента укажи текущую фазу явно, например:

```text
Реализуй этап 3 по docs/EVENT_AGENT_IMPLEMENTATION_CONTEXT.md и docs/EVENT_STAGE_03_EVENT_MANAGEMENT_TZ.md.
```

## Какой Этап Реализуется
- Текущий этап всегда задается пользователем отдельно.
- На момент последней правки документации этапы 1-4 уже реализованы. Перед этапом 5 нужно выполнить stage 4.5: `docs/EVENT_STAGE_04_5_ACCESS_PERMISSIONS_RESTRICTIONS_TZ.md`, если он еще не применен.
- Если этап не указан, остановись и спроси, какой `EVENT_STAGE_*_TZ.md` нужно реализовать.
- Не реализуй будущие этапы заранее, кроме минимального кода, без которого текущий этап не импортируется или не проходит typecheck.
- Tests не писать и не чинить до этапа 10, кроме случая, когда пользователь явно просит тесты.

## Source Of Truth
- Общий план: `docs/EVENT_MODULE_IMPLEMENTATION_PLAN.md`.
- ТЗ текущего этапа: `docs/EVENT_STAGE_XX_*_TZ.md`.
- Модельные изменения: `docs/EVENT_MODEL_CHANGELOG.md`.
- Gateway/Server contract: `docs/SERVER_GATEWAY_EVENT_INTEGRATION.md`.
- Rating/Balancer contract: `docs/EXTERNAL_BALANCER_RANKER_INTEGRATION.md`.
- Legacy/reference only: `docs/WORK.md`, `docs/SERVICES_AND_USECASES.md`.

При расхождении между файлами приоритет такой:

1. Явное сообщение пользователя в текущей задаче.
2. ТЗ текущего этапа.
3. `EVENT_AGENT_IMPLEMENTATION_CONTEXT.md`.
4. `EVENT_MODULE_IMPLEMENTATION_PLAN.md`.
5. Integration docs.
6. Legacy/reference docs только как справочный материал.

## Главные Инварианты
- Event Service не является публичным REST API. REST находится в Gateway.
- Event Service предоставляет внутренние RPC-команды через RabbitMQ/FastStream.
- Event Service не обращается в Server Service напрямую.
- Gateway передает `AccessDataRequest` и необходимые payload-данные: members, role set, rating set, integrations, custom/open ratings.
- В Event Service не должно быть `ServerClient`, `SpaceClient`, `IdentityClient`.
- Прямые внешние queue clients Event Service: `RatingClient`, `MixBalancerClient`, `TournamentBalancerClient`.
- Локальный `organizer` имеет полную власть над своим event независимо от server permissions.
- Server permissions нужны только для создания event и внешних admin override-сценариев.
- Restrictions применяются из `access_data.restriction_mask`.
- Permission/restriction masks должны интерпретироваться по canonical enum order из Server Service `src/infra/postgre/static/permissions.py` и `restrictions.py`; event permissions начинаются с `event_create` на bit 24.
- Подроли не поддерживаются в текущем ТЗ: не принимать, не хранить, не валидировать, не отправлять `subrole_ids`/`subroles`.
- `rating.effective.calculate` опционален.
- `rating.match.process` опционален.
- Alembic не синхронизировать, миграции вне этих ТЗ.

## Работа С Существующей Моделью
- Реализация идет по уже существующим моделям, DTO, репозиториям и таблицам Event Service.
- Не проектировать параллельную новую схему, если текущие сущности можно расширить небольшим понятным изменением.
- Новые поля, enum values, DTO, repo methods или сущности добавлять только если текущая модель не выражает обязательный сценарий этапа.
- Предпочитать минимальное расширение существующей сущности новой сущности.
- Каждое изменение ORM/DTO/enum/repository contract обязательно документировать в `docs/EVENT_MODEL_CHANGELOG.md` в том же изменении.
- Если текущий этап не менял модельный контракт, добавить в `EVENT_MODEL_CHANGELOG.md` запись `Без изменений модели`.
- `EVENT_MODEL_CHANGELOG.md` не является migration notes и не требует Alembic.

## DTO И Repo Правила
- DTO лежат в `src/core/models/<entity>.py`.
- ORM лежат в `src/infra/postgre/models/<entity>.py` и называются `*Model`.
- Repo protocols лежат в `src/core/interfaces/repo/<entity>.py`.
- Repo implementations лежат в `src/infra/postgre/repo/<entity>.py`.
- Для сохраняемых сущностей использовать `*Create`, `*Read`, опциональный `*Update`.
- `*Create` не должен требовать ORM/DB generated fields: `id`, timestamps, computed/server-only fields.
- `*Read` содержит сохраненное состояние, включая `id` и server fields.
- `*Update` создавать только если есть осмысленные изменяемые поля.
- Не добавлять unsuffixed ORM aliases в `src.infra.postgre.models` ради stale imports.
- `src/core/models/__init__.py` должен оставаться пустым; импортировать DTO/enums из конкретных модулей.
- Relationships используют `lazy="raise"`; repository `get(...)` должен иметь `load_*` flags и `selectinload(...)` options.
- Не мутировать frozen DTO. Для изменений использовать `*Update` или repo patch/update methods.
- Использовать современную типизацию: `X | None`, `A | B`, `list[T]`, `dict[K, V]`, `set[T]`, `tuple[...]`, `type[T]`.

## Lifecycle И Single-Game MVP
- Single-game MVP важнее турниров.
- Для single-pass событий допустим flow `CREATED -> REGISTRATION -> FORMATION -> IN_PROGRESS -> COMPLETED`.
- Для ongoing одиночных игр не использовать `FORMATION`/`IN_PROGRESS` как global lock всего event.
- В ongoing single-game event регистрация, выборки, team formation jobs, игроки и матчи имеют собственные статусы.
- Завершение одного single match не завершает event автоматически.
- Event завершается только явной organizer/admin командой и только если нет active matches/блокирующих операций.
- Занятость игрока определяется через наличие игрока в активной выборке, связанной с незавершенным матчем.
- Игроки из такой активной выборки исключаются из новых выборок, если параллельное участие запрещено.
- Для ongoing одиночных игр один раз создать и дальше переиспользовать single-game контейнер `Bracket -> Stage -> StageGroup`; каждый цикл создает новый `Match -> MatchSlot` внутри него.

## Team Formation И Rating Snapshot
- `Draft` в этом проекте означает выборку игроков `selection`/`draft`, а не только captain draft.
- Автоматическое формирование команд использует rating snapshot и внешний balancer.
- Варианты балансировки/распределения команд в этапе 5 хранить временно в Redis, а не в PostgreSQL.
- Не создавать ORM-модели, PostgreSQL таблицы или repository contracts для `team_formation_variant`/`team_formation_variant_player`.
- В PostgreSQL можно сохранять только долговечные сущности: `Draft`, итоговые `Team`/`TeamPlayer` после выбора варианта и, если уже есть подходящая модель, минимальный статус job. Payload вариантов и metrics остаются Redis cache data.
- Redis key должен быть привязан к `event_id`, `draft_id` и `job_id`; variants должны иметь TTL. Если variants истекли, use case должен вернуть понятную ошибку и предложить запустить formation заново.
- Redis integration для этапа 5 повторяет паттерн `mixtura-backend-server`: `RedisSessionManager` на `redis.asyncio.Redis` + `ConnectionPool.from_url(env.redis.url)`, регистрация `redis_engine` в FastStream lifespan через `context.set_global("redis_engine", redis_engine)`, DI через `get_redis_session(redis_engine: Annotated[RedisSessionManager, Context()])`.
- Не копировать server-specific `RedisRepository` cookie helpers; в Event Service нужен purpose-specific `TeamFormationVariantStore`.
- Если `rating.effective.calculate` включен, использовать `effective_rating`.
- Если `rating.effective.calculate` выключен, использовать open-rating snapshot как calculated rating с явным source.
- `PlayerRole.rating` в balancer request заполняется calculated rating from snapshot, не обязательно effective rating из ranker.
- Для manual team formation и captain draft role assignment/rating snapshot приходят с клиента/Gateway payload.
- Event Service валидирует и сохраняет этот payload, но не обращается за ним в Server Service.

## Captain Draft
- Captain draft реализуется только на этапе 9 и не блокирует single-game MVP.
- Captain draft работает поверх существующей `Draft`/selection.
- Не добавлять отдельные `CaptainDraftSession`, `CaptainDraftPick`, `Captain`, если текущие `Draft`/`DraftedPlayer`/`Team` выражают сценарий.
- Капитан определяется через `DraftedPlayer.is_captain`.
- `Team` формируются постепенно по мере выбора игроков капитанами.
- Финальный состав должен быть доступен как `TeamPlayer`.

## FastStream/RabbitMQ Patterns
- Использовать паттерны из Server Service reference, зафиксированные в этапе 2.
- Broker: `RabbitBroker(env.rabbit.url, middlewares=[exc_middleware], default_channel=Channel(prefetch_count=10))`.
- Использовать `ExceptionMiddleware`.
- Использовать агрегирующий `RabbitRouter`.
- Lifespan должен управлять `DatabaseSessionManager`.
- Response envelope: `ResponseMessage[T]`, `ErrorResponse`, `StatusResponse`.
- Dependency wiring через `Annotated[..., Depends(...)]` и `Context()`.
- Не создавать handlers-заглушки будущих этапов. Handler появляется вместе с реализованным use case текущего этапа.

## Порядок Работы Агента
1. Прочитать этот файл.
2. Прочитать `EVENT_MODULE_IMPLEMENTATION_PLAN.md`.
3. Прочитать ТЗ текущего этапа.
4. Прочитать integration docs, если этап касается Gateway/Server/Rating/Balancer contracts.
5. Осмотреть существующий код и модели перед изменениями.
6. Реализовать минимальный объем текущего этапа.
7. Обновить `EVENT_MODEL_CHANGELOG.md`, если менялся model contract, или добавить `Без изменений модели`.
8. Не трогать Alembic.
9. Запустить проверку, указанную в ТЗ этапа, обычно `uv run mypy src`.
10. В финальном ответе перечислить измененные файлы, проверку и оставшиеся ограничения.

## Команды
- Install/sync dependencies: `uv sync`.
- Typecheck: `uv run mypy src`.
- Tests только с этапа 10: `uv run pytest`.
- Focused tests: `uv run pytest tests/path.py::test_name`.

## Known Baseline Caveats
- Старые tests/conftest и service imports могут быть stale до этапа 10.
- `start.py` и Docker entrypoint ранее ссылались на отсутствующие модули; исправлять это только когда требует текущий этап.
- Не добавлять backward compatibility aliases для legacy `src.domain.*` или unsuffixed ORM imports.
