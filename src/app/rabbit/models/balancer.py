from uuid import UUID

from pydantic import BaseModel

from src.core.models.balancer import MixBalancerResult, TournamentBalancerResult


class BalancerResponse(BaseModel):
    status: int
    message: MixBalancerResult | TournamentBalancerResult
