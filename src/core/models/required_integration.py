from __future__ import annotations

from typing import Optional, TYPE_CHECKING
from uuid import UUID

from pydantic import BaseModel, ConfigDict

if TYPE_CHECKING:
    from .event import Event


class RequiredIntegration(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)
    id: UUID
    provider_id: UUID
    event_id: UUID
    event: Optional[Event] = None


class RequiredIntegrationCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)
    provider_id: UUID
    event_id: UUID


class RequiredIntegrationUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)
    pass
