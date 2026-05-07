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
