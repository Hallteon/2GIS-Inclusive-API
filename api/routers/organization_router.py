import logging

from typing import List

from http import HTTPStatus
from fastapi import APIRouter, HTTPException, File, UploadFile, Depends
from fastapi.responses import FileResponse, JSONResponse

from sqlalchemy.ext.asyncio import AsyncSession

from api.database import get_async_session
from api.services.internal.organization_service import (OrganizationService, ImageService,
                                                        OrganizationCategoryService)

from api.schemas.organization_schemes import (OrganizationCreateSchema, OrganizationReadSchema,
                                              OrganizationCategoryReadScheme)


router = APIRouter(prefix='/organizations',
                   tags=['Organizations'])

logger = logging.getLogger(__name__)


@router.post('/images/create', response_model=int)
async def create_image(image: UploadFile = File(...),
                       session: AsyncSession = Depends(get_async_session)):
    """Роут для создания изображения.

    Args:
        image (UploadFile): изображение
        session (AsyncSession): асинхронная сессия

    Returns:
        int: идентификатор созданного изображения
    """

    try:
        image_dict = await ImageService(session=session).create_image(image=image)

        return image_dict['id']

    except HTTPException:
        raise

    except Exception as e:
        logger.exception('Unexpected error in create_image: %s', e)
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail='Unexpected error while creating image'
        )


@router.get('/images/get/{image_id}')
async def get_image(image_id: int,
                    session: AsyncSession = Depends(get_async_session)):
    """Роут для получения изображения.

    Args:
        image_id (int): идентификатор изображения
        session (AsyncSession): асинхронная сессия

    Returns:
        : идентификатор созданного изображения
    """

    try:
        image_dict = await ImageService(session=session).get_image(entity_id=image_id)

        if not image_dict:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail='Image not found'
            )

        return FileResponse(
            image_dict['filepath'],
            headers={'Cache-Control': 'max-age=1800'}
        )

    except HTTPException:
        raise

    except Exception as e:
        logger.exception('Unexpected error in get_image: %s', e)
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail='Unexpected error while getting image'
        )


@router.delete('/images/delete/{image_id}', response_model=bool)
async def delete_image(image_id: int,
                       session: AsyncSession = Depends(get_async_session)):
    """Роут для удаления изображения.

    Args:
        image_id (int): идентификатор изображения
        session (AsyncSession): асинхронная сессия

    Returns:
        bool: удалилось или нет?
    """

    try:
        is_image_deleted = await ImageService(session=session).delete_image(entity_id=image_id)

        if not is_image_deleted:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail='Image not found or could not be deleted'
            )

        return JSONResponse(
            status_code=HTTPStatus.OK,
            content={'message': f'Image {image_id} deleted'}
        )

    except HTTPException:
        raise

    except Exception as e:
        logger.exception('Unexpected error in delete_image: %s', e)

        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail='Unexpected error while deleting image'
        )


@router.post('/create', response_model=int)
async def create_organization(organization: OrganizationCreateSchema,
                              session: AsyncSession = Depends(get_async_session)):
    try:
        organization_dict = await OrganizationService(session=session).create_organization(entity_data=organization.dict())

        if not organization_dict:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail='Organization could not be created'
            )

        return organization_dict['id']

    except HTTPException:
        raise

    except Exception as e:
        logger.exception('Unexpected error in create_organization: %s', e)
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail='Unexpected error while creating organization'
        )


@router.get('/get/{organization_id}', response_model=OrganizationReadSchema)
async def get_organization(organization_id: int,
                           session: AsyncSession = Depends(get_async_session)):
    """Роут для получения организации.

    Args:
        organization_id (int): идентификатор организации
        session (AsyncSession): асинхронная сессия

    Returns:
        OrganizationReadSchema: схема организации
    """

    try:
        organization_dict = await OrganizationService(session=session).get_organization(entity_id=organization_id)

        if not organization_dict:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail='Organization not found'
            )

        return OrganizationReadSchema(**organization_dict)

    except HTTPException:
        raise

    except Exception as e:
        logger.exception('Unexpected error in get_organization: %s', e)
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail='Unexpected error while getting organization'
        )


@router.delete('/delete/{organization_id}', response_model=bool)
async def delete_organization(organization_id: int,
                       session: AsyncSession = Depends(get_async_session)):
    """Роут для удаления организации.

    Args:
        organization_id (int): идентификатор организации
        session (AsyncSession): асинхронная сессия

    Returns:
        bool: удалилось или нет?
    """

    try:
        is_organization_deleted = await OrganizationService(session=session).delete_organization(entity_id=organization_id)

        if not is_organization_deleted:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail='Organization not found or could not be deleted'
            )

        return JSONResponse(
            status_code=HTTPStatus.OK,
            content={'message': f'Organization {organization_id} deleted'}
        )

    except HTTPException:
        raise

    except Exception as e:
        logger.exception('Unexpected error in delete_organization: %s', e)

        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail='Unexpected error while deleting organization'
        )


@router.get('/categories', response_model=List[OrganizationCategoryReadScheme])
async def get_all_organization_categories(session: AsyncSession = Depends(get_async_session)):
    try:
        all_categories = await OrganizationCategoryService(session=session).get_all_categories()
        category_schemes = []

        for category_dict in all_categories:
            category_schemes.append(OrganizationCategoryReadScheme(**category_dict))

        return category_schemes

    except HTTPException:
        raise

    except Exception as e:
        logger.exception('Unexpected error in get_all_organization_categories: %s', e)

        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail='Unexpected error while getting all categories'
        )
