from fastapi import APIRouter

from api.routers.blind_router import router as blind_router
from api.routers.route_router import router as route_router


router = APIRouter()

router.include_router(route_router)
router.include_router(blind_router)