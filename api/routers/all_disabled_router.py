import logging
from typing import List

from http import HTTPStatus
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from api.database import get_async_session
from api.services.external.warning_service import WarningService


router = APIRouter(prefix='/disabled',
                   tags=['Every disabled people'])

logger = logging.getLogger(__name__)


@router.get('/warnings/get', response_model=List[str])
async def get_warnings(latitude: str = Query(description='Широта'),
                       longitude: str = Query(description='Долгота'),
                       session: AsyncSession = Depends(get_async_session)):
    try:
        weather_warnings = await WarningService().get_weather_warnings(lat=float(latitude),
                                                                       lon=float(longitude))

        return weather_warnings

    except HTTPException:
        raise

    except Exception as e:
        logger.exception('Unexpected error in get_warnings: %s', e)
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail='Unexpected error while getting warnings'
        )