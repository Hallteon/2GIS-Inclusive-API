import logging

from typing import List, Optional

from http import HTTPStatus
from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from api.database import get_async_session
from api.services.internal.event_service import EventService, EventCategoryService
from api.schemas.event_schemes import (EventCreateScheme, EventReadScheme, EventCategoryReadScheme,
                                       EventCategoryCreateScheme)


router = APIRouter(prefix='/events',
                   tags=['Events'])

logger = logging.getLogger(__name__)



@router.post('/create', response_model=int)
async def create_event(event: EventCreateScheme,
                       session: AsyncSession = Depends(get_async_session)):
    """Роут для создания события.

    Args:
        event (EventCreateScheme): событие
        session (AsyncSession): асинхронная сессия

    Returns:
        int: идентификатор события
    """

    try:
        event_dict = await EventService(session=session).create_event(entity_data=event.dict())

        if not event_dict:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail='Event could not be created'
            )

        return event_dict['id']

    except HTTPException:
        raise

    except Exception as e:
        logger.exception('Unexpected error in create_event: %s', e)
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail='Unexpected error while creating event'
        )


@router.get('/get/{event_id}', response_model=EventReadScheme)
async def get_event(event_id: int,
                    session: AsyncSession = Depends(get_async_session)):
    """Роут для получения события.

    Args:
        event_id (int): идентификатор события
        session (AsyncSession): асинхронная сессия

    Returns:
        EventReadScheme: схема события
    """

    try:
        event_dict = await EventService(session=session).get_event(entity_id=event_id)

        if not event_dict:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail='Event not found'
            )

        return EventReadScheme(**event_dict)

    except HTTPException:
        raise

    except Exception as e:
        logger.exception('Unexpected error in get_event: %s', e)
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail='Unexpected error while getting event'
        )


@router.post('/categories/create', response_model=int)
async def create_event_category(category: EventCategoryCreateScheme,
                                session: AsyncSession = Depends(get_async_session)):
    """Роут для создания категории.

    Args:
        category (EventCategoryCreateScheme): категория
        session (AsyncSession): асинхронная сессия

    Returns:
        int: идентификатор категории
    """

    try:
        category_dict = await EventCategoryService(session=session).create_category(entity_data=category.dict())

        if not category_dict:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail='Category could not be created'
            )

        return category_dict['id']

    except HTTPException:
        raise

    except Exception as e:
        logger.exception('Unexpected error in create_category: %s', e)
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail='Unexpected error while creating category'
        )


@router.get('/get_by_name', response_model=EventCategoryReadScheme)
async def get_event_category_by_name(name: str,
                                     session: AsyncSession = Depends(get_async_session)):
    """Роут для получения категории.

    Args:
        name (str): название
        session (AsyncSession): асинхронная сессия

    Returns:
        EventCategoryReadScheme: схема категории
    """

    try:
        category_dict = await EventCategoryService(session=session).get_event_by_name(event_name=name)

        if not category_dict:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail='Category not found'
            )

        return EventCategoryReadScheme(**category_dict)

    except HTTPException:
        raise

    except Exception as e:
        logger.exception('Unexpected error in get_category: %s', e)
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail='Unexpected error while getting category'
        )



