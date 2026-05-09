from uuid import UUID

from pydantic import BaseModel, Field

from src.core.commands.access_data import AccessDataRequest
from src.core.commands.pagination import PaginationRequest
from src.core.models.application import ApplicationStatus


class SubmitApplicationCommand(BaseModel):
    access_data: AccessDataRequest
    event_id: UUID
    integration_ids: list[UUID] = Field(default_factory=list)
    filled_fields: dict[UUID, str] = Field(default_factory=dict)
    role_priorities: dict[UUID, int] = Field(default_factory=dict)


class GetApplicationCommand(BaseModel):
    application_id: UUID
    access_data: AccessDataRequest


class ReviewApplicationCommand(BaseModel):
    access_data: AccessDataRequest
    application_id: UUID
    status: ApplicationStatus


class ListApplicationsCommand(BaseModel):
    event_id: UUID
    access_data: AccessDataRequest
    status: ApplicationStatus | None = None
    pagination: PaginationRequest = PaginationRequest()
