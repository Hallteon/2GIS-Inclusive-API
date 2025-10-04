import base64
import logging

from http import HTTPStatus
from fastapi import APIRouter, HTTPException, File, UploadFile, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.database import get_async_session
from api.services.internal.blind_service import BlindHelpService


router = APIRouter(prefix='/blinds',
                   tags=['Blinds'])

logger = logging.getLogger(__name__)


@router.post('/summary/create', response_model=str)
async def create_image_summary(description: str = None,
                                   image: UploadFile = File(...),
                                   session: AsyncSession = Depends(get_async_session)):
    """Роут для создания контакта клиента.

    Args:
        image (UploadFile): изображение от пользователя
        description: (str): описание изображения от пользователя
        session (AsyncSession): асинхронная сессия

    Returns:
        str: тифлокомментарий от AI по изображению и описанию необходимого слепому человеку объекта
    """

    try:
        contents = await image.read()
        base64_encoded = base64.b64encode(contents).decode('utf-8')

        image_description = await BlindHelpService(session=session).create_description(image=base64_encoded,
                                                                                       description=description)

        return image_description

    except HTTPException:
        raise

    except Exception as e:
        logger.exception('Unexpected error in create_image_summary: %s', e)
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail='Unexpected error while creating image description'
        )


@router.post('/map/position/get', response_model=str)
async def get_map_mark_location(image: UploadFile = File(...),
                                session: AsyncSession = Depends(get_async_session)):
    """Роут для создания контакта клиента.

    Args:
        image (UploadFile): изображение от пользователя
        session (AsyncSession): асинхронная сессия

    Returns:
        str: позиция маркера на карте
    """

    try:
        contents = await image.read()
        base64_encoded = base64.b64encode(contents).decode('utf-8')

        image_description = await BlindHelpService(session=session).get_user_map_position(image=base64_encoded)

        return image_description

    except HTTPException:
        raise

    except Exception as e:
        logger.exception('Unexpected error in get_map_mark_location: %s', e)
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail='Unexpected error while getting mark location'
        )