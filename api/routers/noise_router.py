import logging

from typing import List

from http import HTTPStatus
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from api.database import get_async_session
from api.services.internal.noise_service import NoiseService
from api.utils.cache_utils import cache_response


router = APIRouter(prefix='/noise',
                   tags=['Noise'])

logger = logging.getLogger(__name__)


@router.get('/points', response_model=List[dict])
@cache_response(ttl=60 * 30)
async def get_noise_points(count: int = Query(description='Количество точек'),
                           session: AsyncSession = Depends(get_async_session)):
    try:
        noise_points = await NoiseService().get_noise_points(count=count)

        return noise_points

    except Exception as e:
        logger.exception('Unexpected error in get_noise_points: %s', e)
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail='Unexpected error while getting noise map points'
        )
