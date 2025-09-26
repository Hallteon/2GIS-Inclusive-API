from fastapi import APIRouter

from api.routers.blind_routes import router as project_router


router = APIRouter()

router.include_router(project_router)