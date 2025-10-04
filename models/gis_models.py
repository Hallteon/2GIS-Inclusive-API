import datetime

from typing import Optional, List, Dict, Any, Set

from api.database import Base
from sqlalchemy.orm import Mapped, relationship, mapped_column
from sqlalchemy import (Column, Integer, String, DateTime,
                        ForeignKey, Text, Float)


class BaseModel(Base):
    __abstract__ = True

    def as_dict(self, nested: Optional[Dict[str, Any]] = None, exclude: Optional[Set[str]] = None,
                auto_load: bool = False) -> Dict[str, Any]:
        if nested is None:
            nested = {}
        if exclude is None:
            exclude = set()

        result = {}

        # Базовые поля
        for column in self.__table__.columns:
            if column.name in exclude:
                continue
            value = getattr(self, column.name)
            if isinstance(value, datetime.datetime):
                value = value.isoformat()
            result[column.name] = value

        # Обработка отношений
        for relationship_name, nested_params in nested.items():
            if relationship_name in exclude:
                continue

            try:
                # Пытаемся получить отношение
                relationship_obj = getattr(self, relationship_name)

                # Если auto_load=True и отношение не загружено, пытаемся загрузить
                if auto_load:
                    from sqlalchemy.orm.attributes import instance_state
                    state = instance_state(self)
                    if relationship_name in state.unloaded:
                        # Загружаем отношение
                        state.session.refresh(self, [relationship_name])
                        relationship_obj = getattr(self, relationship_name)

                if relationship_obj is None:
                    result[relationship_name] = None
                elif isinstance(relationship_obj, list):
                    if nested_params is True:
                        result[relationship_name] = [item.as_dict() for item in relationship_obj]
                    elif isinstance(nested_params, dict):
                        result[relationship_name] = [item.as_dict(**nested_params) for item in relationship_obj]
                else:
                    if nested_params is True:
                        result[relationship_name] = relationship_obj.as_dict()
                    elif isinstance(nested_params, dict):
                        result[relationship_name] = relationship_obj.as_dict(**nested_params)

            except Exception as e:
                # Если произошла ошибка (например, сессия закрыта), устанавливаем None
                result[relationship_name] = None

        return result


class Route(BaseModel):
    __tablename__ = "routes"

    id: Mapped[int] = Column(Integer, primary_key=True)

    name: Mapped[Optional[str]] = Column(String, nullable=True, default=None)
    description: Mapped[Optional[str]] = Column(Text, nullable=True, default=None)

    points: Mapped[List['Point']] = relationship('Point', back_populates='route',
                                                 cascade="all, delete-orphan")

    created_datetime: Mapped[datetime.datetime] = Column(DateTime, default=datetime.datetime.now())

    def __str__(self):
        return f'Маршрут "{self.name}": {self.description} - {self.created_datetime}'


class Point(BaseModel):
    __tablename__ = 'points'

    id: Mapped[int] = Column(Integer, primary_key=True)

    name: Mapped[Optional[str]] = Column(String, nullable=True, default=None)
    description: Mapped[Optional[str]] = Column(Text, nullable=True, default=None)

    latitude: Mapped[float] = Column(Float)
    longitude: Mapped[float] = Column(Float)

    category_id: Mapped[int] = mapped_column(ForeignKey('categories.id'))
    category: Mapped['Category'] = relationship('Category', back_populates='points')

    route_id: Mapped[int] = mapped_column(ForeignKey('routes.id'))
    route: Mapped['Route'] = relationship('Route', back_populates='points')

    def __str__(self):
        return f'Точка маршрута {self.name} с долготой {self.longitude} и широтой {self.latitude}'


class Category(BaseModel):
    __tablename__ = 'categories'

    id: Mapped[int] = Column(Integer, primary_key=True)
    name: Mapped[str] = Column(String, unique=True)

    points: Mapped[List['Point']] = relationship('Point', back_populates='category')

    def __str__(self):
        return self.name