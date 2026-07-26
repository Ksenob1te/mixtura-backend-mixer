from faststream.rabbit import RabbitRouter

from src.app.rabbit.models.application import (
    ApplicationDetailResponse,
    ApplicationListItem,
    ApplicationReviewResult,
    ApplicationSubmitResult,
    GetApplicationMessage,
    ListApplicationsMessage,
    ReviewApplicationMessage,
    SubmitApplicationMessage,
)
from src.core.commands.application import (
    GetApplicationCommand,
    ListApplicationsCommand,
    ReviewApplicationCommand,
    SubmitApplicationCommand,
)
from src.core.response import ResponseMessage
from src.dependency import ApplicationServiceDependency

router = RabbitRouter()


@router.subscriber(queue="event.application.submit")
async def submit_application(
    data: SubmitApplicationMessage,
    service: ApplicationServiceDependency,
) -> ResponseMessage[ApplicationSubmitResult]:
    command = SubmitApplicationCommand(**data.model_dump())
    result = await service.submit(command)
    return ResponseMessage(status=200, message=ApplicationSubmitResult(**result.model_dump()))


@router.subscriber(queue="event.application.get")
async def get_application(
    data: GetApplicationMessage,
    service: ApplicationServiceDependency,
) -> ResponseMessage[ApplicationDetailResponse]:
    command = GetApplicationCommand(**data.model_dump())
    result = await service.get(command)
    return ResponseMessage(status=200, message=ApplicationDetailResponse(**result.model_dump()))


@router.subscriber(queue="event.application.list")
async def list_applications(
    data: ListApplicationsMessage,
    service: ApplicationServiceDependency,
) -> ResponseMessage[list[ApplicationListItem]]:
    command = ListApplicationsCommand(**data.model_dump())
    result = await service.get_list(command)
    return ResponseMessage(status=200, message=[ApplicationListItem(**r.model_dump()) for r in result])


@router.subscriber(queue="event.application.review")
async def review_application(
    data: ReviewApplicationMessage,
    service: ApplicationServiceDependency,
) -> ResponseMessage[ApplicationReviewResult]:
    command = ReviewApplicationCommand(**data.model_dump())
    result = await service.review(command)
    return ResponseMessage(status=200, message=ApplicationReviewResult(**result.model_dump()))
