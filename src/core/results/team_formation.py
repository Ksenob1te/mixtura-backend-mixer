from uuid import UUID

from pydantic import BaseModel


class TeamFormationVariant(BaseModel):
    id: UUID
    draft_id: UUID
    quality_uniformity: float | None = None
    quality_fairness: float | None = None
    quality_role_points: float | None = None
    quality_role_fairness: float | None = None
    is_selected: bool = False
