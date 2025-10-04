from typing import List

from fastapi.params import Depends

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from api.database import get_async_session

from models.gis_models import Event, EventCategory


class EventDAO:
    __slots__ = ('_db', 'session')

    def __init__(self, session: AsyncSession = Depends(get_async_session)):
        self._db = Event
        self.session = session

    async def get_by_id(self, entity_id: int) -> dict | None:
        stmt = select(self._db).options(
            selectinload(Event.category)
        ).filter(self._db.id == entity_id)
        entity_query = await self.session.execute(stmt)

        entity = entity_query.scalars().first()

        if entity:
            return entity.as_dict(nested={'category': True})

        return None

    async def create(self, data: dict) -> dict:
        event_obj = self._db(**data)

        self.session.add(event_obj)
        await self.session.commit()

        return event_obj.as_dict()


class EventCategoryDAO:
    __slots__ = ('_db', 'session')

    def __init__(self, session: AsyncSession = Depends(get_async_session)):
        self._db = EventCategory
        self.session = session

    async def create(self, data: dict) -> dict:
        category_obj = self._db(**data)

        self.session.add(category_obj)
        await self.session.commit()

        return category_obj.as_dict()

    async def get_by_name(self, name: str) -> dict | None:
        query = select(self._db).where(self._db.name == name)
        result = await self.session.execute(query)

        category = result.scalar_one_or_none()

        return category.as_dict() if category else None


