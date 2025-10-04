import datetime

from typing import Optional, List
from pydantic import BaseModel, Field, field_validator


class EventCategoryReadScheme(BaseModel):
    id: int = Field(..., description='Идентификатор точки')
    name: str = Field(..., description='Название события')


class EventCategoryCreateScheme(BaseModel):
    name: str = Field(..., description='Название события')


class EventReadScheme(BaseModel):
    id: int = Field(..., description='Идентификатор точки')

    name: Optional[str] = Field(None, description='Название маршрута')

    category: Optional[EventCategoryReadScheme] = Field(None, description='Категория')

    address: Optional[str] = Field(None, description='Адрес')
    comment: Optional[str] = Field(None, description='Комментарий')

    start_datetime: Optional[datetime.datetime] = Field(None, description='Время начала')
    end_datetime: Optional[datetime.datetime] = Field(None, description='Время конца')

    work: Optional[str] = Field(None, description='Описание')
    worker: Optional[str] = Field(None, description='Кто делает')

    geom: Optional[list] = Field(None, description='Геометрические метки')

    # category_id: Optional[int] = Field(None, description='Категория')


class EventCreateScheme(BaseModel):
    category_id: Optional[int] = Field(None, description='Идентификатор категории')

    address: Optional[str] = Field(None, description='Адрес')
    comment: Optional[str] = Field(None, description='Комментарий')

    start_datetime: Optional[datetime.datetime] = Field(None, description='Время начала')
    end_datetime: Optional[datetime.datetime] = Field(None, description='Время конца')

    work: Optional[str] = Field(None, description='Описание')
    worker: Optional[str] = Field(None, description='Кто делает')

    geom: Optional[list] = Field(None, description='Геометрические метки')

    @field_validator('start_datetime', 'end_datetime', mode='before')
    @classmethod
    def convert_aware_to_naive_utc(cls, v):  # type: ignore
        if v is None:
            return v

        # Если пришла строка - преобразуем в datetime
        if isinstance(v, str):
            try:
                v = datetime.datetime.fromisoformat(v.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                # Если не получается распарсить, оставляем как есть -
                # Pydantic сам выбросит ValidationError
                return v

        # Если это datetime объект с временной зоной
        if hasattr(v, 'tzinfo') and v.tzinfo is not None:
            # Конвертируем в UTC и удаляем информацию о временной зоне
            v = v.astimezone(datetime.timezone.utc).replace(tzinfo=None)

        return v

