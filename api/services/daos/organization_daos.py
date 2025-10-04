from typing import List

from fastapi.params import Depends

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from api.database import get_async_session

from models.gis_models import Organization, OrganizationCategory, Image


class OrganizationDAO:
    __slots__ = ('_db', 'session')

    def __init__(self, session: AsyncSession = Depends(get_async_session)):
        self._db = Organization
        self.session = session

    async def get_by_id(self, entity_id: int) -> dict | None:
        stmt = select(self._db).filter(self._db.id == entity_id)
        entity_query = await self.session.execute(stmt)

        entity = entity_query.scalars().first()

        if entity:
            return entity.as_dict(nested={'category': True})

        return None

    async def create(self, data: dict) -> dict:
        route_obj = self._db(**data)

        self.session.add(route_obj)
        await self.session.commit()

        return route_obj.as_dict()

    async def update(self, entity_id: int, data: dict) -> dict | None:
        organization = await self.get_by_id(entity_id)

        if not organization:
            return None

        for key, value in data.items():
            if value != None:
                setattr(organization, key, value)

                if key.endswith('_id'):
                    self.session.expire(organization, [key.rstrip('_id')])

        await self.session.commit()

        updated_organization = await self.get_by_id(entity_id=entity_id)

        return updated_organization

    async def delete(self, entity_id: int) -> bool:
        try:
            organization = await self.session.get(self._db, entity_id)

            if not organization:
                return False

            await self.session.delete(organization)
            await self.session.commit()

            return True

        except Exception as e:
            await self.session.rollback()
            raise e


class ImageDAO:
    __slots__ = ('_db', 'session')

    def __init__(self, session: AsyncSession = Depends(get_async_session)):
        self._db = Image
        self.session = session

    async def get_by_id(self, entity_id: int) -> dict | None:
        stmt = select(self._db).filter(self._db.id == entity_id)
        entity_query = await self.session.execute(stmt)

        entity = entity_query.scalars().first()

        if entity:
            return entity.as_dict()

        return None

    async def create(self, data: dict) -> dict:
        image_obj = self._db(**data)

        self.session.add(image_obj)
        await self.session.commit()

        return image_obj.as_dict()

    async def delete(self, entity_id: int) -> bool:
        try:
            image = await self.session.get(self._db, entity_id)

            if not image:
                return False

            await self.session.delete(image)
            await self.session.commit()

            return True

        except Exception as e:
            await self.session.rollback()
            raise e


class OrganizationCategoryDAO:
    __slots__ = ('_db', 'session')

    def __init__(self, session: AsyncSession = Depends(get_async_session)):
        self._db = OrganizationCategory
        self.session = session

    async def get_all_ordered(self, order_by: str = 'id') -> List[dict]:
        stmt = select(self._db).order_by(getattr(self._db, order_by))
        result = await self.session.execute(stmt)

        return [res.as_dict() for res in result.scalars().all()]