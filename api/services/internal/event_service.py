from typing import List

from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.database import get_async_session
from api.services.daos.event_daos import EventCategoryDAO, EventDAO


class EventService:
    def __init__(self, session: AsyncSession = Depends(get_async_session)):
        self.session = session

    async def get_event(self, entity_id: int) -> dict| None:
        event_dict = await EventDAO(session=self.session).get_by_id(entity_id=entity_id)

        return event_dict

    async def get_events_random(self, events_count: int) -> List[dict]:
        random_events = await EventDAO(session=self.session).get_random_list(count=events_count)

        return random_events

    async def create_event(self, entity_data: dict) -> dict:
        event_dict = await EventDAO(session=self.session).create(data=entity_data)

        return event_dict


class EventCategoryService:
    def __init__(self, session: AsyncSession = Depends(get_async_session)):
        self.session = session

    async def create_category(self, entity_data: dict) -> dict:
        category_dict = await EventCategoryDAO(session=self.session).create(data=entity_data)

        return category_dict

    async def get_event_by_name(self, event_name: str) -> dict | None:
        event_dict = await EventCategoryDAO(session=self.session).get_by_name(name=event_name)

        return event_dict