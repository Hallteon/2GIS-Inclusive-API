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


@router.post('/create_image_description', response_model=str)
async def create_image_description(description: str = None,
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
        logger.exception('Unexpected error in create_image_description: %s', e)
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail='Unexpected error while creating image description'
        )