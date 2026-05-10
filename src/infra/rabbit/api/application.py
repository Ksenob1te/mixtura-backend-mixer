from faststream.rabbit import RabbitRouter

from src.core.commands.application import (
    GetApplicationCommand,
    ListApplicationsCommand,
    ReviewApplicationCommand,
    SubmitApplicationCommand,
)
from src.core.response import ResponseMessage, StatusResponse
from src.dependency import ApplicationServiceDependency

router = RabbitRouter()


@router.subscriber(queue="event.application.submit")
async def submit_application(
    data: SubmitApplicationCommand,
    service: ApplicationServiceDependency,
) -> ResponseMessage[dict]:
    result = await service.submit(data)
    return ResponseMessage(status=200, message=result)


@router.subscriber(queue="event.application.get")
async def get_application(
    data: GetApplicationCommand,
    service: ApplicationServiceDependency,
) -> ResponseMessage[dict]:
    result = await service.get(data)
    return ResponseMessage(status=200, message=result)


@router.subscriber(queue="event.application.list")
async def list_applications(
    data: ListApplicationsCommand,
    service: ApplicationServiceDependency,
) -> ResponseMessage[list[dict]]:
    result = await service.get_list(data)
    return ResponseMessage(status=200, message=result)


@router.subscriber(queue="event.application.review")
async def review_application(
    data: ReviewApplicationCommand,
    service: ApplicationServiceDependency,
) -> ResponseMessage[dict]:
    result = await service.review(data)
    return ResponseMessage(status=200, message=result)
