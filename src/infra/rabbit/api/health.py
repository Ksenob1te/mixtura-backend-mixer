import logging

from faststream.rabbit import RabbitRouter

from src.core.commands.health import HealthRequest
from src.core.response import ResponseMessage, StatusResponse

router = RabbitRouter()
logger = logging.getLogger(__name__)


@router.subscriber(queue="event.health")
async def health_check(
    data: HealthRequest,
) -> ResponseMessage[StatusResponse]:
    return ResponseMessage(status=200, message=StatusResponse())
