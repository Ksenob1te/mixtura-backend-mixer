from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from ..exceptions import IntegrityForeignException, IntegrityUniqueException, IntegrityUnknownException


class BaseRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def _flush(self) -> None:
        try:
            await self._session.flush()
        except IntegrityError as exc:
            sql_state = getattr(exc.orig, "sqlstate", None)
            if sql_state == "23503":
                raise IntegrityForeignException() from exc
            if sql_state == "23505":
                raise IntegrityUniqueException() from exc
            raise IntegrityUnknownException() from exc
