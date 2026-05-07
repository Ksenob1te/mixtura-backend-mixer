from faststream.rabbit import RabbitRouter

from .health import router as HealthController
from .event import router as EventController
from .organizer import router as OrganizerController
from .application import router as ApplicationController
from .player import router as PlayerController

router = RabbitRouter()

router.include_router(HealthController)
router.include_router(EventController)
router.include_router(OrganizerController)
router.include_router(ApplicationController)
router.include_router(PlayerController)
