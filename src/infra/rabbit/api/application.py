from faststream.rabbit import RabbitRouter

from src.core.commands.application import (
    GetApplicationCommand,
    ListApplicationsCommand,
    ReviewApplicationCommand,
    SubmitApplicationCommand,
)
from src.core.response import ResponseMessage, StatusResponse
from src.core.usecases.application import (
    GetApplicationUseCase,
    ListApplicationsUseCase,
    ReviewApplicationUseCase,
    SubmitApplicationUseCase,
)
from src.dependency import (
    GetApplicationUseCaseDependency,
    ListApplicationsUseCaseDependency,
    ReviewApplicationUseCaseDependency,
    SubmitApplicationUseCaseDependency,
)

router = RabbitRouter()


@router.subscriber(queue="event.application.submit")
async def submit_application(
    data: SubmitApplicationCommand,
    use_case: SubmitApplicationUseCaseDependency,
) -> ResponseMessage[dict]:
    result = await use_case(data)
    return ResponseMessage(status=200, message=result)


@router.subscriber(queue="event.application.get")
async def get_application(
    data: GetApplicationCommand,
    use_case: GetApplicationUseCaseDependency,
) -> ResponseMessage[dict]:
    result = await use_case(data)
    return ResponseMessage(status=200, message=result)


@router.subscriber(queue="event.application.list")
async def list_applications(
    data: ListApplicationsCommand,
    use_case: ListApplicationsUseCaseDependency,
) -> ResponseMessage[list[dict]]:
    result = await use_case(data)
    return ResponseMessage(status=200, message=result)


@router.subscriber(queue="event.application.review")
async def review_application(
    data: ReviewApplicationCommand,
    use_case: ReviewApplicationUseCaseDependency,
) -> ResponseMessage[dict]:
    result = await use_case(data)
    return ResponseMessage(status=200, message=result)
