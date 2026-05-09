# ТЗ Для Агента: Этап 2. Внешние Контракты Модуля

## Цель
Описать и реализовать базовый RPC-контур Event Service: FastStream app, handlers, dependency wiring, healthcheck и контракты взаимодействия с Gateway, Rating Service и Balancer Services. После этапа сервис должен стартовать локально и импортировать RPC handlers без ссылок на старые entrypoints.

## Общий Контекст
- Event Service не публикует REST API. Gateway принимает HTTP-запросы, а Event Service предоставляет внутренние RPC-команды через RabbitMQ/FastStream.
- Event Service не обращается в Server Service напрямую. Gateway получает контекст доступа, участников, role set, rating set и custom/open ratings из Server Service и передает Event Service только нужный payload.
- Для внутренних RPC-команд `AccessDataRequest` заменяет JWT.
- Event Service принимает `access_data.permission_mask`, но не вычисляет permissions самостоятельно.
- Локальный organizer в Event Service имеет полную власть над своим мероприятием независимо от server permissions.
- Server permissions нужны для создания мероприятия и server-admin override-сценариев над чужими мероприятиями.

## FastStream Reference Из Server Service
Reference-проект изучен: `C:\Users\dmela\Desktop\desktop\programming\mixtura-backend-server`. Event Service должен повторить механики FastStream/RabbitMQ из Server Service, но адаптировать пути под новую архитектуру `src/core`, `src/infra/rabbit`, `src/infra/postgre` и не возвращаться к legacy `src.domain`.

Файлы Server Service, которые использовались как источник паттернов:

- `src/domain/main.py`: создание `ExceptionMiddleware`, `RabbitBroker`, подключение общего router, lifespan и `FastStream` app.
- `src/domain/api/__init__.py`: агрегирующий `RabbitRouter`, который включает routers из модулей API.
- `src/domain/api/member.py`, `src/domain/api/core.py`, `src/domain/api/game_role.py`, `src/domain/api/rating.py`, `src/domain/api/custom.py`: стиль RPC handlers и queue naming.
- `src/dependency.py`: FastStream dependency wiring через `Annotated[..., Depends(...)]` и `Context()`.
- `src/domain/models/request.py`: `AccessDataRequest` и `PaginationRequest`.
- `src/domain/models/response.py`: `ResponseMessage[T]`, `ErrorResponse`, `StatusResponse`.
- `src/domain/exceptions.py`: domain exceptions со status code.
- `src/infra/postgre/engine.py`: async `DatabaseSessionManager` и commit/rollback lifecycle.
- `start.py`: минимальный запуск `asyncio.run(app.run())` после настройки логирования.

Конкретные решения, которые нужно перенести в Event Service:

- Создать один FastStream app module для Event Service, например `src/infra/rabbit/main.py` или другой согласованный путь, но не использовать старый `src.domain.main`.
- Создавать `ExceptionMiddleware()` и регистрировать handler для доменных исключений Event Service с `publish=True`.
- В exception handler откатывать `DatabaseSession`, если он есть в dependency context, и возвращать `ResponseMessage[ErrorResponse]` со status code исключения.
- Создавать `RabbitBroker(env.rabbit.url, middlewares=[exc_middleware], default_channel=Channel(prefetch_count=10))`.
- Подключать handlers через один агрегирующий `RabbitRouter`, аналогично `broker.include_router(api.router)` в Server Service.
- Разделить handlers по файлам предметных команд, например `event.py`, `application.py`, `draft.py`, `team_formation.py`, `single_match.py`, `tournament_bracket.py`, и собрать их в `src/infra/rabbit/api/__init__.py` через `RabbitRouter().include_router(...)`.
- Каждый handler объявлять через `@router.subscriber(queue="...")` или `@router.subscriber("...")`; в Event Service лучше использовать единый стиль с именованным аргументом `queue="..."`.
- Handler должен принимать command DTO первым аргументом и use case/service dependency вторым аргументом, как в Server Service: `async def handler(data: Command, use_case: UseCaseDependency) -> ResponseMessage[Result]`.
- Для списков использовать `pydantic.TypeAdapter(list[ResponseDTO]).validate_python(...)`, как в Server Service.
- Для одиночных DTO использовать `ResponseDTO.model_validate(...)`.
- Для успешных ответов использовать `ResponseMessage(status=200, message=...)`.
- Для команд без payload результата использовать `StatusResponse(status="ok")` или локальный аналог, совместимый с Server Service.
- Создать `src/dependency.py` или эквивалентный dependency module для Event Service: session provider через `Context()`, repository providers, use case providers и type aliases `XUseCaseDependency = Annotated[XUseCase, Depends(get_x_use_case)]`.
- В lifespan создать `DatabaseSessionManager(env.postgres.url)`, положить его в context как `session_manager`, на shutdown закрыть, если `opened`.
- Если Redis на этом этапе не нужен Event Service, не добавлять Redis dependency только ради сходства с Server Service.
- Entry point должен импортировать новый FastStream app и запускать `asyncio.run(app.run())`; удалить ссылки на отсутствующие `src.infra.static` и `src.domain.main`.

Что не переносить из Server Service:

- Не переносить пакетную структуру `src.domain.*` в Event Service.
- Не переносить прямые Server Service handlers как зависимости Event Service.
- Не добавлять Redis, если для текущих Event Service use cases он не нужен.
- Не копировать request/response DTO Server Service внутрь Event Service шире, чем нужно для совместимого `AccessDataRequest`, `PaginationRequest`, `ResponseMessage`, `ErrorResponse`, `StatusResponse`.

Queue naming для Event Service должен быть явным и согласованным. На этапе 2 нужно зафиксировать каталог имен и реализовать только инфраструктуру RPC, healthcheck и минимальные handlers, нужные для уже готовой функциональности. Остальные feature handlers добавлять по мере реализации соответствующих этапов, а не делать пустые заглушки заранее.

Single-game MVP queues:

- `event.create`
- `event.get`
- `event.list_public`
- `event.list_private`
- `event.update`
- `event.activate`
- `event.registration.open`
- `event.registration.close`
- `event.cancel`
- `event.organizer.list`
- `event.organizer.add`
- `event.organizer.remove`
- `event.application.submit`
- `event.application.get`
- `event.application.review`
- `event.application.list`
- `event.player.list`
- `event.player.status.update`
- `event.player.remove`
- `event.draft.create`
- `event.draft.get`
- `event.draft.list`
- `event.team_formation.run`
- `event.team_formation.get`
- `event.team_formation.choose`
- `event.team.list`
- `event.match.setup`
- `event.match.result.record`
- `event.match.get`
- `event.match.list`
- `event.complete`

Tournament queues для этапа 8:

- `event.tournament.bracket.generate`
- `event.tournament.bracket.get`
- `event.tournament.standings.get`
- `event.tournament.round.generate`
- `event.tournament.stage.complete`
- `event.tournament.complete`

Captain draft queues для этапа 9:

- `event.captain_draft.create`
- `event.captain_draft.start`
- `event.captain_draft.get`
- `event.captain_draft.pick`
- `event.captain_draft.skip`
- `event.captain_draft.cancel`
- `event.captain_draft.complete`

Service queues:

- `event.health`

## AccessDataRequest
```python
AccessDataRequest(
    member_id=UUID | None,
    server_id=UUID,
    permission_mask=int,
    restriction_mask=int,
)
```

## Server-Side Permissions
- `event_create`: создавать мероприятия в пространстве, если создание не открыто всем участникам.
- `event_admin_view`: просматривать непубличные мероприятия и административные данные без локальной роли organizer.
- `event_admin_update`: административно менять настройки и статус любого мероприятия пространства.
- `event_admin_manage_organizers`: произвольно добавлять, удалять и заменять organizers любого мероприятия пространства.
- `event_admin_manage_players`: административно управлять заявками, участниками и составами любого мероприятия пространства.
- `event_admin_manage_bracket`: административно менять сетку, стадии, группы, посев и результаты матчей любого мероприятия пространства.
- `event_admin_cancel`: административно отменять любое мероприятие пространства.
- `event_admin_complete`: административно завершать стадии и мероприятия при ручном вмешательстве.

## Restrictions
- `server_ban`: запрещает создание, вступление, подачу заявки и organizer-действия в мероприятиях пространства.
- `mix_ban`: запрещает участие в одиночном матче или mix-событии.
- `tournament_ban`: запрещает участие в турнирном событии.
- `self_edit_name`: не влияет на Event Service, если сервис не меняет nickname участника.

## Gateway -> Event Service RPC
- Описать command DTO для синхронных операций: создать событие, прочитать событие, обновить событие, открыть регистрацию, отменить событие, настроить регистрацию, подать заявку, обработать заявку, получить списки заявок/игроков, создать выборку, запустить формирование команд, выбрать вариант команд, сгенерировать сетку, зафиксировать результат матча.
- Commands, которым нужен контекст пользователя или пространства, должны включать `access_data`.
- Public list/get команды могут принимать `server_id`, pagination/filter поля и не требовать `access_data`, если возвращают только публичные события и публичные поля.
- Private list/get команды должны принимать `access_data` и проверять членство в пространстве.
- Команды управления мероприятием должны проверять локальную роль organizer или соответствующее server-admin override permission.

## Gateway -> Server Service Данные
- Gateway вызывает `member.by_user` и передает Event Service `AccessDataRequest`.
- Gateway вызывает `server.get_info` и передает Event Service нужные данные пространства, если use case не может работать только по `server_id`.
- Gateway вызывает `member.get`/`member.list` и передает Event Service участников, необходимых для ручного выбора или проверки.
- Gateway вызывает `role_set.get_by_server` и передает доступные игровые роли пространства.
- Gateway вызывает `rating_set.get_by_server` и передает рейтинговую шкалу.
- Gateway вызывает `custom.get_by_member` и передает open/custom ratings для rating snapshot.

## Rating Service Контракты
- `rating.effective.calculate` опционален и включается настройкой Event Service.
- Если `rating.effective.calculate` включен, Event Service перед формированием команд отправляет open-rating snapshot и получает `effective_rating` по `member_id + role_id`.
- Если `rating.effective.calculate` выключен, Event Service использует open-rating snapshot как расчетный рейтинг и сохраняет источник.
- `rating.match.process` опционален и включается настройкой Event Service.
- Если `rating.match.process` выключен, Event Service сохраняет локальный match result payload/snapshot и не публикует его в рейтинг-сервис.

## Balancer Service Контракты
- `mix_balance_service.balance` используется для одиночного матча или двух команд.
- `tournament_balance_service.balance` используется для турнирного формирования нескольких команд.
- `mixtura_balancer_tournament` публикует прогресс в `mix_balance_service.balance.progress` с `correlation_id=str(draft_id)`.
- В `PlayerRole.rating` передается расчетный рейтинг из snapshot, приведенный к `int`.
- Priority semantics отличаются между балансировщиками, поэтому Event Service должен нормализовать priorities отдельно для каждого клиента.

## Задачи
- Реализовать FastStream/RabbitMQ оформление по конкретным решениям из раздела `FastStream Reference Из Server Service`.
- Создать или привести к рабочему состоянию FastStream app под Event Service без использования legacy `src.domain.main`.
- Создать `ExceptionMiddleware`, domain exception handler с rollback session и `ResponseMessage[ErrorResponse]`.
- Создать агрегирующий `RabbitRouter` для Event handlers и подключить его к `RabbitBroker`.
- Создать dependency module с providers для DB session, repositories и use cases через `Annotated[..., Depends(...)]`.
- Описать DTO команд в `src/core/commands`.
- Описать DTO результатов сложных операций в `src/core/results`.
- Описать протоколы клиентов внешних сервисов в `src/core/interfaces/clients`.
- Реализовать RPC-инфраструктуру в `src/infra/rabbit` и handlers только для healthcheck/готовой функциональности. Feature handlers следующих этапов добавлять вместе с соответствующими use cases, сохраняя queue names, dependencies и response envelope из этого документа.
- Реализовать healthcheck queue `event.health`.
- Убрать ссылки на несуществующие `src.infra.static` и старые entrypoints.

## Не Делать
- Не реализовывать публичный REST.
- Не обращаться напрямую в Server Service из Event Service.
- Не синхронизировать Alembic.
- Не реализовывать полноценную бизнес-логику этапов 3-9, если она не нужна для wiring.
- Не писать и не исправлять тесты; тестирование вынесено в этап 10.

## Критерии Приемки
- Сервис стартует локально или FastStream app импортируется без ошибок из нового Event Service entrypoint.
- RPC handlers импортируются через агрегирующий `RabbitRouter`.
- В entrypoint/wiring нет ссылок на `src.domain` и `src.infra.static`.
- Контракты access, rating и balancer отражены в DTO/protocols.
- Успешные handlers возвращают `ResponseMessage(status=200, message=...)`.
- Domain exceptions превращаются в `ResponseMessage[ErrorResponse]` через FastStream `ExceptionMiddleware`.

## Команды Проверки
- `uv run mypy src`
