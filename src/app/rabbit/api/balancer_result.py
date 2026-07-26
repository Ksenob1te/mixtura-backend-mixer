from typing import Annotated
from uuid import UUID

from faststream import Context
from faststream.rabbit import RabbitRouter

from src.app.rabbit.models.balancer import BalancerResponse
from src.dependency import TeamFormationServiceDependency

router = RabbitRouter()


@router.subscriber(queue="mixer_service.balancer.result")
async def balancer_result_handler(
    body: dict,
    correlation_id: Annotated[str, Context("message.correlation_id")],
    service: TeamFormationServiceDependency,
) -> None:
    task_id = UUID(correlation_id)
    response = BalancerResponse.model_validate(body)
    await service.complete_formation(task_id, response.message)
