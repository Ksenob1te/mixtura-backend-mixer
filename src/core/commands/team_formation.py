from uuid import UUID

from pydantic import BaseModel

from src.core.commands.access_data import AccessDataRequest


class RunTeamFormationCommand(BaseModel):
    access_data: AccessDataRequest
    draft_id: UUID


class GetTeamFormationCommand(BaseModel):
    draft_id: UUID
    access_data: AccessDataRequest | None = None


class ChooseTeamFormationVariantCommand(BaseModel):
    access_data: AccessDataRequest
    draft_id: UUID
    variant_id: UUID
