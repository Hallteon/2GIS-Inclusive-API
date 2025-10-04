import uuid

from typing import List

from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import UploadFile

from api.database import get_async_session
from api.services.daos.organization_daos import OrganizationDAO, ImageDAO, OrganizationCategoryDAO
from api.utils.image_upload_service import ImageUploadService

from settings import config_parameters


class OrganizationService:
    def __init__(self, session: AsyncSession = Depends(get_async_session)):
        self.session = session

    async def get_organization(self, entity_id: int) -> dict | None:
        organization = await OrganizationDAO(session=self.session).get_by_id(entity_id=entity_id)

        return organization

    async def create_organization(self, entity_data: dict) -> dict:
        organization = await OrganizationDAO(session=self.session).create(data=entity_data)

        return organization

    async def update_organization(self, entity_id: int, entity_data: dict) -> dict | None:
        updated_organization = await OrganizationDAO(session=self.session).update(entity_id=entity_id,
                                                                                  data=entity_data)

        return updated_organization

    async def delete_organization(self, entity_id: int) -> bool:
        organization_deleted = await OrganizationDAO(session=self.session).delete(entity_id=entity_id)

        return organization_deleted


class ImageService:
    def __init__(self, session: AsyncSession = Depends(get_async_session)):
        self.session = session

    def _generate_unique_filename(self, original_name):
        extension = original_name.split('.')[-1] if '.' in original_name else 'txt'
        unique_id = uuid.uuid4()

        return f"{unique_id}.{extension}"

    async def get_image(self, entity_id: int) -> dict | None:
        image = await ImageDAO(session=self.session).get_by_id(entity_id=entity_id)

        return image

    async def create_image(self, image: UploadFile) -> dict:
        image_filename = self._generate_unique_filename(original_name=image.filename)
        image_path = f'{config_parameters.MEDIA_DIR}/{config_parameters.ORGANIZATION_IMAGE_DIR}/{image_filename}'

        await ImageUploadService().save_image(image=image, image_filepath=image_path)

        image = await ImageDAO(session=self.session).create(data={'filepath': image_path})

        return image

    async def delete_image(self, entity_id: int) -> bool:
        image = await ImageDAO(session=self.session).get_by_id(entity_id=entity_id)

        if not image:
            return False

        image_deleted = await ImageUploadService().delete_image(image_filepath=image.get('filepath'))

        if image_deleted:
            await ImageDAO(session=self.session).delete(entity_id=entity_id)

        return image_deleted


class OrganizationCategoryService:
    def __init__(self, session: AsyncSession = Depends(get_async_session)):
        self.session = session

    async def get_all_categories(self) -> List[dict]:
        all_categories = await OrganizationCategoryDAO(session=self.session).get_all_ordered()

        return all_categories
