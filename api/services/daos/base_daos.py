from typing import Any

from fastapi.params import Depends

from sqlalchemy import select, Sequence
from sqlalchemy.ext.asyncio import AsyncSession

from api.database import get_async_session

from models.gis_models import *


class BaseDAO:
    __slots__ = ('_db', 'session')

    def __init__(self, db: Any, session: AsyncSession = Depends(get_async_session)):
        self._db = db
        self.session = session

    async def create(self, data: dict) -> dict:
        entity_obj = self._db(**data)

        self.session.add(entity_obj)
        await self.session.commit()

        return entity_obj

    async def get_all(self) -> Sequence[dict]:
        entities_query = await self.session.execute(select(Project))
        entities = entities_query.scalars().all()

        return entities

    async def get_by_id(self, entity_id: int):
        entity_query = await self.session.execute(select(self._db).filter(self._db.id == entity_id))
        entity = entity_query.scalars().first()

        return entity

    async def update(self, entity_id: int, data: dict) -> dict:
        entity = await self.get_by_id(entity_id=entity_id)

        for key, value in data.items():
            if value != None:
                setattr(entity, key, value)

                if key.endswith('_id'):
                    self.session.expire(entity, [key.rstrip('_id')])

        await self.session.commit()

        updated_entity = await self.get_by_id(entity_id=entity_id)

        return updated_entity

    async def delete(self, entity_id: int) -> bool:
        entity = await self.get_by_id(entity_id=entity_id)

        if entity:
            await self.session.delete(entity)
            await self.session.commit()

            return True

        return False
