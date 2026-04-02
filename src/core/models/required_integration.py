from __future__ import annotations
from pydantic import BaseModel, ConfigDict
from typing import Optional, TYPE_CHECKING
from uuid import UUID

if TYPE_CHECKING:
    from .event import Event


class RequiredIntegration(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)
    id: UUID
    name: str
    event_id: UUID
    event: Optional[Event] = None
