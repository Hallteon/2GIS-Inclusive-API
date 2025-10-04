from typing import Optional, List

from datetime import datetime
from pydantic import BaseModel, Field


class CategoryReadSchema(BaseModel):
    id: int = Field(..., description='Идентификатор категории')

    name: str = Field(..., description='Название категории')


class PointCreateSchema(BaseModel):
    name: Optional[str] = Field(None, description='Название маршрута')
    description: Optional[str] = Field(None, description='Описание маршрута')

    category_id: Optional[int] = Field(None, description='Идентификатор категории')

    latitude: float = Field(..., description='Широта')
    longitude: float = Field(..., description='Долгота')


class PointReadSchema(BaseModel):
    id: int = Field(..., description='Идентификатор точки')

    name: Optional[str] = Field(None, description='Название маршрута')
    description: Optional[str] = Field(None, description='Описание маршрута')

    category: Optional[CategoryReadSchema] = Field(None, description='Категория')

    latitude: float = Field(..., description='Широта')
    longitude: float = Field(..., description='Долгота')


class RouteReadSchema(BaseModel):
    id: int = Field(..., description='Идентификатор маршрута')

    name: Optional[str] = Field(None, description='Название маршрута')
    description: Optional[str] = Field(None, description='Описание маршрута')

    points: List[PointReadSchema] = Field(..., description='Точки маршрута')

    created_datetime: datetime = Field(..., description='Дата и время создания маршрута')


class RouteCreateSchema(BaseModel):
    name: Optional[str] = Field(None, description='Название маршрута')
    description: Optional[str] = Field(None, description='Описание маршрута')

    points: List[PointCreateSchema] = Field(..., description='Точки маршрута')


# class RouteUpdateSchema(BaseModel):
#     name: Optional[str] = Field(None, description='Название маршрута')
#     description: Optional[str] = Field(None, description='Описание маршрута')
#
#     points: Optional[List[PointCreateSchema]] = Field(None, description='Точки маршрута')


class CategoryReadScheme(BaseModel):
    id: int = Field(None, description='Идентификатор события')

    name: str = Field(..., description='Название события')


class EventCreateScheme(BaseModel):
    name: str = Field(..., description='Название события')
