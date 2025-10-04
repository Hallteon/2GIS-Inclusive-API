import logging

from typing import List

from http import HTTPStatus
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from api.database import get_async_session
from api.services.internal.route_service import RouteService, CategoryService
from api.schemas.route_schemas import (RouteCreateSchema, RouteReadSchema, PointReadSchema,
                                       CategoryReadSchema)

from models.gis_models import Route


router = APIRouter(prefix='/routes',
                   tags=['Routes'])

logger = logging.getLogger(__name__)


@router.post('/create', response_model=int)
async def create_route(route: RouteCreateSchema,
                       session: AsyncSession = Depends(get_async_session)):
    """Роут для создания маршрута.

    Args:
        route (RouteCreateSchema): маршрут
        session (AsyncSession): асинхронная сессия

    Returns:
        int: идентификатор маршута
    """

    try:
        route_dict = await RouteService(session=session).create_route(entity_data=route.dict())

        if not route_dict:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail='Route could not be created'
            )

        return route_dict['id']

    except HTTPException:
        raise

    except Exception as e:
        logger.exception('Unexpected error in create_route: %s', e)
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail='Unexpected error while creating route'
        )


@router.get('/get/{route_id}', response_model=RouteReadSchema)
async def get_route(route_id: int,
                    session: AsyncSession = Depends(get_async_session)):
    """Роут для получения маршрута.

    Args:
        route_id (int): идентификатор маршрута
        session (AsyncSession): асинхронная сессия

    Returns:
        RouteReadSchema: схема маршрута
    """

    try:
        route_dict = await RouteService(session=session).get_route(entity_id=route_id)

        if not route_dict:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail='Route not found'
            )

        return RouteReadSchema(**route_dict)

    except HTTPException:
        raise

    except Exception as e:
        logger.exception('Unexpected error in get_route: %s', e)
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail='Unexpected error while getting route'
        )


@router.delete('/delete/{route_id}', response_model=bool)
async def delete_route(route_id: int,
                       session: AsyncSession = Depends(get_async_session)):
    """Роут для удаления маршрута.

    Args:
        route_id (int): идентификатор маршрута
        session (AsyncSession): асинхронная сессия

    Returns:
        bool: удалилось или нет?
    """

    try:
        is_route_deleted = await RouteService(session=session).delete_route(entity_id=route_id)

        if not is_route_deleted:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail='Route not found or could not be deleted'
            )

        return JSONResponse(
            status_code=HTTPStatus.OK,
            content={'message': f'Route {route_id} deleted'}
        )

    except HTTPException:
        raise

    except Exception as e:
        logger.exception('Unexpected error in delete_route: %s', e)

        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail='Unexpected error while deleting route'
        )


@router.get('/categories', response_model=List[CategoryReadSchema])
async def get_all_point_categories(session: AsyncSession = Depends(get_async_session)):
    try:
        all_categories = await CategoryService(session=session).get_all_categories()

        return all_categories

    except HTTPException:
        raise

    except Exception as e:
        logger.exception('Unexpected error in get_all_point_categories: %s', e)

        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail='Unexpected error while getting all categories'
        )

