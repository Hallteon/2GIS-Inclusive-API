import datetime

from typing import Optional, List

from api.database import Base
from sqlalchemy.orm import Mapped, relationship, mapped_column
from sqlalchemy import (Column, Integer, String, DateTime,
                        ForeignKey, Text, Float)


class Route(Base):
    __tablename__ = "routes"

    id: Mapped[int] = Column(Integer, primary_key=True)

    name: Mapped[Optional[str]] = Column(String, nullable=True, default=None)
    description: Mapped[Optional[str]] = Column(Text, nullable=True, default=None)

    points: Mapped[List['Point']] = relationship('Point', back_populates='route')

    created_datetime: Mapped[datetime.datetime] = Column(DateTime, default=datetime.datetime.now())

    def __str__(self):
        return f'Маршрут "{self.name}": {self.description} - {self.created_datetime}'


class Point(Base):
    __tablename__ = 'points'

    id: Mapped[int] = Column(Integer, primary_key=True)

    name: Mapped[Optional[str]] = Column(String, nullable=True, default=None)
    description: Mapped[Optional[str]] = Column(Text, nullable=True, default=None)

    latitude: Mapped[float] = Column(Float)
    longitude: Mapped[float] = Column(Float)

    route_id: Mapped[int] = mapped_column(ForeignKey('routes.id'))
    route: Mapped['Route'] = relationship('Route', back_populates='points')

    def __str__(self):
        return f'Точка маршрута {self.name} с долготой {self.longitude} и широтой {self.latitude}'


class Event(Base):
    __tablename__ = 'events'

    id: Mapped[int] = Column(Integer, primary_key=True)

    name: Mapped[str] = Column(String, unique=True)
    description: Mapped[Optional[str]] = Column(Text, nullable=True, default=None)

    latitude: Mapped[float] = Column(Float)
    longitude: Mapped[float] = Column(Float)

    def __str__(self):
        return f'Мероприятие {self.name}: {self.description}'

