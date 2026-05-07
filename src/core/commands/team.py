from uuid import UUID

from pydantic import BaseModel

from src.core.commands.access_data import AccessDataRequest
from src.core.commands.pagination import PaginationRequest


class ListTeamsCommand(BaseModel):
    event_id: UUID
    access_data: AccessDataRequest | None = None
    pagination: PaginationRequest = PaginationRequest()
