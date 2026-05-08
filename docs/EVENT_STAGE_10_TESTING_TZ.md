# ТЗ Для Агента: Этап 10. Тестирование

## Цель
Сформировать тестовый слой для Event Service, покрывающий чистую доменную логику, репозитории, use cases и RPC handlers. После этапа ключевые сценарии Event Service должны быть проверяемы локально и в CI без реальных Gateway/Server/Rating/Balancer сервисов.

## Общий Контекст
- Репозиторий использует `uv` и Python `>=3.13`.
- `uv run ...` создает или использует локальную `.venv` из `uv.lock`.
- `pytest.ini` включает `asyncio_mode = auto` и dotenv loading из `.env`.
- Repository-тесты используют PostgreSQL testcontainers и требуют Docker.
- Текущий baseline раньше ломался на stale imports в `tests/conftest.py`; тестовый слой должен быть переписан под текущие event-модели.
- Тестирование специально вынесено в этап 10; этапы 1-9 не должны были писать или чинить tests.

## Команды
- Установка зависимостей: `uv sync`.
- Typecheck: `uv run mypy src`.
- Все тесты: `uv run pytest`.
- Focused test: `uv run pytest tests/path.py::test_name`.
- Collect only: `uv run pytest --collect-only`.

## Unit Tests
- Глобальные переходы event lifecycle по `event_flow.ini`.
- Независимые статусы регистрации, выборок, team formation jobs, игроков и матчей.
- Валидация заявок: обязательные поля, роли, интеграции, уникальность, restrictions.
- Winner detection: score, draw, technical loss.
- Single-match setup и completion без автоматического завершения event.
- Генераторы сложных сеток: single elimination, double elimination, round robin, swiss.
- Standings: очки, wins/losses/draws, score diff, tie-breakers.
- Captain draft: порядок выбора, запрет двойного выбора, завершение и материализация команд.
- Rating snapshot mapping: open rating, optional effective rating, source tracking.
- Balancer request mapping: priority normalization для mix и tournament balancer.

## Repository Tests
- Создание/чтение `Event` с `server_id`.
- Создание/чтение `Organizer`.
- Создание/чтение application aggregate: application, filled fields, integrations, selected roles.
- Создание/чтение event players.
- Создание/чтение draft/selection. Team formation variants не проверять как repository entities, потому что они временно хранятся в Redis.
- Создание/чтение teams/team players.
- Создание/чтение single-match bracket/stage/group/match/slots/scores.
- Создание/чтение tournament bracket/stages/groups/matches/placements.
- Создание/чтение captain draft state на `Draft`/`DraftedPlayer`, включая `DraftedPlayer.is_captain` и связь выбранных игроков с `Team`.
- Проверка `load_*` flags и `lazy="raise"` relationships.

## Use Case Tests
- Create event flow.
- Open/close registration settings flow.
- Join flow with `use_application=false`.
- Submit application flow with `use_application=true`.
- Approve/reject/waitlist flow.
- Team formation flow with effective rating enabled.
- Team formation flow with effective rating disabled.
- Choose team formation variant flow.
- Single-match setup flow.
- Single-match result flow without event completion.
- Explicit event completion flow.
- Tournament bracket generation flow.
- Tournament match result and advancement flow.
- Complete tournament event flow.
- Captain draft flow.
- Organizer access without server permissions.
- Server-admin override access with event admin permissions.
- Restrictions blocking participation or admin actions.

## RPC Handler Tests
- Использовать FastStream test client или прямой вызов handlers с fake dependencies.
- Не требовать реальный Gateway.
- Не требовать реальные Server/Rating/Balancer сервисы.
- Проверять DTO parsing и error response mapping.
- Проверять, что handlers прокидывают `access_data` в use cases.
- Проверять optional rating flags.

## Test Doubles
- Fake repositories для use case tests.
- Fake Redis/team formation variant store для use case tests этапа 5.
- Fake RatingClient с режимами enabled/disabled и deterministic responses.
- Fake MixBalancerClient и Fake TournamentBalancerClient, возвращающие variants с метриками.
- Fake Gateway payload builders для `AccessDataRequest`, role set, rating set, members, custom ratings.

## Задачи
- Переписать `tests/conftest.py` под текущий Event Service.
- Разделить tests на unit, repository, use case и RPC handler tests.
- Добавить factories/builders для DTO и ORM моделей.
- Добавить fake clients и fake repositories.
- Зафиксировать marks или skip behavior для Docker-dependent repository tests, если Docker недоступен.
- Довести `uv run pytest --collect-only` до прохождения.

## Не Делать
- Не поднимать реальные Gateway/Server/Rating/Balancer сервисы для обычных tests.
- Не синхронизировать Alembic.
- Не добавлять backward compatibility aliases ради старых tests.

## Критерии Приемки
- `uv run pytest --collect-only` проходит.
- Unit/use case tests не требуют Docker.
- Repository tests используют testcontainers и явно отделены от быстрых tests.
- Основные сценарии Event Service покрыты tests.
- `uv run mypy src` проходит или оставшиеся ошибки явно задокументированы.

## Команды Проверки
- `uv run mypy src`
- `uv run pytest --collect-only`
- `uv run pytest`
