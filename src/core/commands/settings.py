from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from src.core.commands.access_data import AccessDataRequest


class AddIntegrationCommand(BaseModel):
    access_data: AccessDataRequest
    event_id: UUID
    name: str


class RemoveIntegrationCommand(BaseModel):
    access_data: AccessDataRequest
    event_id: UUID
    integration_id: UUID


class AddGameRoleCommand(BaseModel):
    access_data: AccessDataRequest
    event_id: UUID
    game_role_id: UUID
    override_max_count: int | None = None
    override_min_count: int | None = None


class UpdateGameRoleCommand(BaseModel):
    access_data: AccessDataRequest
    event_id: UUID
    selected_role_id: UUID
    override_max_count: int | None = None
    override_min_count: int | None = None


class RemoveGameRoleCommand(BaseModel):
    access_data: AccessDataRequest
    event_id: UUID
    selected_role_id: UUID


class AddCustomFieldCommand(BaseModel):
    access_data: AccessDataRequest
    event_id: UUID
    name: str
    is_private: bool = False
    is_required: bool = False


class UpdateCustomFieldCommand(BaseModel):
    access_data: AccessDataRequest
    event_id: UUID
    field_id: UUID
    name: str | None = None
    is_private: bool | None = None
    is_required: bool | None = None


class RemoveCustomFieldCommand(BaseModel):
    access_data: AccessDataRequest
    event_id: UUID
    field_id: UUID


class UpdateTimeSettingsCommand(BaseModel):
    access_data: AccessDataRequest
    event_id: UUID
    start_time: datetime | None = None
    end_time: datetime | None = None


class GetApplicationFormSettingsCommand(BaseModel):
    event_id: UUID
    access_data: AccessDataRequest
