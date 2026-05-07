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
  2. Добавлены enum-ы: `EventMatchType`, `RegistrationType`, `StageFormat`, `EventPlayerStatus`.
  3. Добавлено поле `server_id: UUID` в `Event`/`EventModel`.
  4. Добавлено поле `status: EventPlayerStatus` в `EventPlayer`/`EventPlayerModel`.
  5. `match_type: str` → `match_type: EventMatchType` (DTO и ORM).
  6. `registration_type: str` → `registration_type: RegistrationType` (DTO и ORM).
  7. `format: str` → `format: StageFormat` в `Stage`/`StageModel` (DTO и ORM).
  8. Все 24 DTO разделены на `*Create`/`*Read` (существующий unsuffixed класс как Read) / опциональный `*Update`.
  9. `BaseRepository` расширен с `Generic[ModelType, DTOType]` до `Generic[ModelType, CreateDTO, ReadDTO, UpdateDTO]`.
  10. Все 24 репозитория и протокола обновлены: `create(dto: *Create) -> *Read`, `update(dto: *Update) -> *Read`.
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
