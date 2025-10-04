from typing import Optional

from pydantic import BaseModel, Field


class OrganizationCategoryReadScheme(BaseModel):
    id: int = Field(..., description='Идентификатор организации')
    name: str = Field(..., description='Название категории')


class OrganizationReadSchema(BaseModel):
    id: int = Field(..., description='Идентификатор организации')

    name: Optional[str] = Field(None, description='Название маршрута')
    description: Optional[str] = Field(None, description='Описание маршрута')

    address: Optional[str] = Field(None, description='Адрес')

    category: Optional[OrganizationCategoryReadScheme] = Field(None, description='Категория')
    image_id: Optional[int] = Field(None, description='Идентификатор изображения')

    latitude: Optional[float] = Field(None, description='Широта')
    longitude: Optional[float] = Field(None, description='Долгота')


class OrganizationCreateSchema(BaseModel):
    name: Optional[str] = Field(None, description='Название маршрута')
    description: Optional[str] = Field(None, description='Описание маршрута')

    address: Optional[str] = Field(None, description='Адрес')

    category_id: Optional[int] = Field(None, description='Идентификатор категории')
    image_id: Optional[int] = Field(None, description='Идентификатор изображения')

    latitude: Optional[float] = Field(None, description='Широта')
    longitude: Optional[float] = Field(None, description='Долгота')


