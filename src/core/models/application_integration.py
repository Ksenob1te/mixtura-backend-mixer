from __future__ import annotations

from typing import Optional, TYPE_CHECKING
from uuid import UUID

from pydantic import BaseModel, ConfigDict

if TYPE_CHECKING:
    from .application import Application


class ApplicationIntegration(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)
    id: UUID
    application_id: UUID
    user_provider_id: UUID
    provider_id: UUID
    provider_name: str
    application: Optional[Application] = None


class ApplicationIntegrationCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)
    application_id: UUID
    user_provider_id: UUID
    provider_id: UUID
    provider_name: str
