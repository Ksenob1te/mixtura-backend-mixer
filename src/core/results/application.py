from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ApplicationRoleItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    role_id: UUID
    game_role_id: UUID | None = None
    priority: int


class ApplicationIntegrationItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    integration_id: UUID
    provider_id: UUID
    provider_name: str


class ApplicationListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    member_id: UUID
    status: str
    is_approved: bool
    created_at: datetime
    roles: list[ApplicationRoleItem] = []
    integrations: list[ApplicationIntegrationItem] = []
