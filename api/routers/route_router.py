import logging

from typing import List, Optional

from http import HTTPStatus
from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from api.database import get_async_session
from api.services.internal.route_service import RouteService, CategoryService, PointService
from api.schemas.route_schemas import (RouteCreateSchema, RouteReadSchema,
                                       CategoryReadSchema, PointCreateSchema, PointReadSchema)


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


@router.get('/points/filter', response_model=List[PointReadSchema])
async def filter_points(category_id: Optional[int] = Query(None, description='Категория'),
                        session: AsyncSession = Depends(get_async_session)):
    try:
        filtered_points = await PointService(session=session).filter_points(category_id=category_id)
        point_schemes = []

        for point in filtered_points:
            point_schemes.append(PointReadSchema(**point))

        return point_schemes

    except HTTPException:
        raise

    except Exception as e:
        logger.exception('Unexpected error in filter_points: %s', e)

        raise HTTPException(

            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,

            detail='Unexpected error while filtering route'

        )


@router.post('/points/create', response_model=int)
async def create_point(point: PointCreateSchema,
                       session: AsyncSession = Depends(get_async_session)):
    try:
        point_dict = await PointService(session=session).create_point(entity_data=point.dict())

        if not point_dict:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail='Point could not be created'
            )

        return point_dict['id']

    except HTTPException:
        raise

    except Exception as e:
        logger.exception('Unexpected error in create_point: %s', e)
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail='Unexpected error while creating point'
        )


@router.get('/points/get/{point_id}', response_model=PointReadSchema)
async def get_point(point_id: int,
                    session: AsyncSession = Depends(get_async_session)):
    """Роут для получения точки.

    Args:
        point_id (int): идентификатор точки
        session (AsyncSession): асинхронная сессия

    Returns:
        PointReadSchema: схема точки
    """

    try:
        point_dict = await PointService(session=session).get_point(entity_id=point_id)

        if not point_dict:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail='Point not found'
            )

        return PointReadSchema(**point_dict)

    except HTTPException:
        raise

    except Exception as e:
        logger.exception('Unexpected error in get_point: %s', e)
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail='Unexpected error while getting point'
        )


@router.delete('/points/delete/{point_id}', response_model=bool)
async def delete_point(point_id: int,
                       session: AsyncSession = Depends(get_async_session)):
    """Роут для удаления точки.

    Args:
        point_id (int): идентификатор точки
        session (AsyncSession): асинхронная сессия

    Returns:
        bool: удалилось или нет?
    """

    try:
        is_point_deleted = await PointService(session=session).delete_point(entity_id=point_id)

        if not is_point_deleted:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail='Point not found or could not be deleted'
            )

        return JSONResponse(
            status_code=HTTPStatus.OK,
            content={'message': f'Point {point_id} deleted'}
        )

    except HTTPException:
        raise

    except Exception as e:
        logger.exception('Unexpected error in delete_point: %s', e)

        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail='Unexpected error while deleting point'
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
        category_schemes = []

        for category_dict in all_categories:
            category_schemes.append(CategoryReadSchema(**category_dict))

        return category_schemes

    except HTTPException:
        raise

    except Exception as e:
        logger.exception('Unexpected error in get_all_point_categories: %s', e)

        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail='Unexpected error while getting all categories'
        )