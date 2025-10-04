from typing import List

from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.database import get_async_session
from api.services.daos.route_daos import RouteDAO, CategoryDAO

from models.gis_models import Route, Category


class RouteService:
    def __init__(self, session: AsyncSession = Depends(get_async_session)):
        self.session = session

    async def get_route(self, entity_id: int) -> dict | None:
        route_obj = await RouteDAO(session=self.session).get_by_id(entity_id=entity_id)

        return route_obj

    async def create_route(self, entity_data: dict) -> dict:
        route = await RouteDAO(session=self.session).create(data=entity_data)

        return route

    async def delete_route(self, entity_id: int) -> bool:
        route_deleted = await RouteDAO(session=self.session).delete(entity_id=entity_id)

        return route_deleted


class CategoryService:
    def __init__(self, session: AsyncSession = Depends(get_async_session)):
        self.session = session

    async def get_all_categories(self) -> List[Category]:
        all_categories = await CategoryDAO(session=self.session).get_all_ordered()

        return all_categories
