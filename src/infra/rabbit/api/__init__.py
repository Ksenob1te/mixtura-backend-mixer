from faststream.rabbit import RabbitRouter

from .health import router as HealthController
from .event import router as EventController
from .organizer import router as OrganizerController
from .application import router as ApplicationController
from .player import router as PlayerController
from .draft import router as DraftController
from .team_formation import router as TeamFormationController
from .team import router as TeamController
from .match import router as MatchController

router = RabbitRouter()

router.include_router(HealthController)
router.include_router(EventController)
router.include_router(OrganizerController)
router.include_router(ApplicationController)
router.include_router(PlayerController)
router.include_router(DraftController)
router.include_router(TeamFormationController)
router.include_router(TeamController)
router.include_router(MatchController)
