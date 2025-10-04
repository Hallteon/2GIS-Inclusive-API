from typing import List

from fastapi.params import Depends

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from api.database import get_async_session

from models.gis_models import Route, Point, Category


class PointDAO:
    def __init__(self, session: AsyncSession = Depends(get_async_session)):
        self.session = session
        self._db = Point

    async def get_by_id(self, entity_id: int) -> dict | None:
        entity_query = await self.session.execute(select(self._db).filter(self._db.id == entity_id))
        entity = entity_query.scalars().first()

        return entity


class RouteDAO:
    __slots__ = ('_db', '_points_db', 'session')

    def __init__(self, session: AsyncSession = Depends(get_async_session)):
        self._db = Route
        self._points_db = Point

        self.session = session

    async def get_by_id(self, entity_id: int) -> dict | None:
        stmt = select(self._db).options(
            selectinload(Route.points).selectinload(Point.category)
        ).filter(self._db.id == entity_id)
        entity_query = await self.session.execute(stmt)

        entity = entity_query.scalars().first()

        if entity:
            return entity.as_dict(nested={'points': {'nested': {'category': True}}})

        return None

    async def create(self, data: dict) -> dict:
        route_points = []
        point_objs = []

        if data.get('points', None):
            route_points.extend(data.get('points'))
            del data['points']

        route_obj = self._db(**data)

        self.session.add(route_obj)

        for point_data in route_points:
            point_obj = self._points_db(**point_data, route=route_obj)

            point_objs.append(point_obj)

        self.session.add_all(point_objs)

        await self.session.commit()

        return route_obj.as_dict()

    async def delete(self, entity_id: int) -> bool:
        try:
            route = await self.session.get(self._db, entity_id)
            if not route:
                return False

            await self.session.delete(route)
            await self.session.commit()

            return True

        except Exception as e:
            await self.session.rollback()
            raise e


class CategoryDAO:
    __slots__ = ('_db', 'session')

    def __init__(self, session: AsyncSession = Depends(get_async_session)):
        self._db = Category
        self.session = session

    async def get_all_ordered(self, order_by: str = 'id') -> List[Category]:
        stmt = select(self._db).order_by(getattr(self._db, order_by))
        result = await self.session.execute(stmt)

        return list(result.scalars().all())