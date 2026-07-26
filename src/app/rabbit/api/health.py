import logging

from faststream.rabbit import RabbitRouter

from src.app.rabbit.models.health import HealthMessage
from src.core.response import ResponseMessage, StatusResponse

router = RabbitRouter()
logger = logging.getLogger(__name__)


@router.subscriber(queue="event.health")
async def health_check(
    data: HealthMessage,
) -> ResponseMessage[StatusResponse]:
    return ResponseMessage(status=200, message=StatusResponse())
