from fastapi import APIRouter

from api.routers.blind_router import router as blind_router
from api.routers.route_router import router as route_router
from api.routers.all_disabled_router import router as disabled_router
from api.routers.organization_router import router as organization_router
from api.routers.event_router import router as event_router
from api.routers.noise_router import router as noise_router


router = APIRouter()

router.include_router(route_router)
router.include_router(blind_router)
router.include_router(disabled_router)
router.include_router(organization_router)
router.include_router(event_router)
router.include_router(noise_router)