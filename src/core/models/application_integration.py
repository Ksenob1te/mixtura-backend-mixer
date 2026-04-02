from __future__ import annotations
from pydantic import BaseModel, ConfigDict
from typing import Optional, TYPE_CHECKING
from uuid import UUID

if TYPE_CHECKING:
    from .application import Application


class ApplicationIntegration(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)
    id: UUID
    application_id: UUID
    user_provider_id: UUID
    application: Optional[Application] = None
