from uuid import UUID

from pydantic import BaseModel

from src.core.commands.access_data import AccessDataRequest
from src.core.commands.pagination import PaginationRequest
from src.core.models.application import ApplicationStatus


class SubmitApplicationCommand(BaseModel):
    access_data: AccessDataRequest
    event_id: UUID
    integration_ids: list[UUID] = []
    filled_fields: dict[UUID, str] = {}
    role_priorities: dict[UUID, int] = {}


class GetApplicationCommand(BaseModel):
    application_id: UUID
    access_data: AccessDataRequest | None = None


class ReviewApplicationCommand(BaseModel):
    access_data: AccessDataRequest
    application_id: UUID
    status: ApplicationStatus


class ListApplicationsCommand(BaseModel):
    event_id: UUID
    access_data: AccessDataRequest | None = None
    status: ApplicationStatus | None = None
    pagination: PaginationRequest = PaginationRequest()
