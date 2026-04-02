from __future__ import annotations
from pydantic import BaseModel, ConfigDict
from typing import Optional, TYPE_CHECKING
from uuid import UUID

if TYPE_CHECKING:
    from .event import Event


class ApplicationCustomField(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)
    id: UUID
    event_id: UUID
    name: str
    is_private: bool
    is_required: bool
    event: Optional[Event] = None
