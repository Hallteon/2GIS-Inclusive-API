import datetime

from api.database import Base
from sqlalchemy.orm import Mapped, relationship, mapped_column
from sqlalchemy import (Column, Integer, String, DateTime, Date,
                        Boolean, ForeignKey, Text, PickleType, Float)


class TrafficFine(Base):
    __tablename__ = "traffic_fines"

    id: Mapped[int] = Column(Integer, primary_key=True)

    camera_fines_count: Mapped[int] = Column(Integer, default=0)
    decisions_made_count: Mapped[int] = Column(Integer, default=0)
    fines_imposed_sum: Mapped[int] = Column(Integer, default=0)
    fines_collected_sum: Mapped[int] = Column(Integer, default=0)

    created_date: Mapped[datetime.date] = Column(Date, default=datetime.date.today())

    def __str__(self):
        return f'Статистика по штрафам на {self.created_date.__str__()}'


class Evacuation(Base):
    __tablename__ = "evacuations"

    id: Mapped[int] = Column(Integer, primary_key=True)

    line_trucks_count: Mapped[int] = Column(Integer, default=0)
    truck_trips_count: Mapped[int] = Column(Integer, default=0)
    evacuations_count: Mapped[int] = Column(Integer, default=0)
    revenue_sum: Mapped[int] = Column(Integer, default=0)

    created_date: Mapped[datetime.date] = Column(Date, default=datetime.date.today())

    def __str__(self):
        return f'Статистика по эвакуациям на {self.created_date.__str__()}'


class TrafficLight(Base):
    __tablename__ = 'traffic_lights'

    id: Mapped[int] = Column(Integer, primary_key=True)

    address: Mapped[str] = Column(String, default='base_address')
    light_type: Mapped[str] = Column(String, default='T.1')
    created_year: Mapped[int] = Column(Integer, default=2015)

    def __str__(self):
        return f'{self.address} - {self.id}, год установки - {self.created_year}'


class Image(Base):
    __tablename__ = 'images'

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    filepath = Column(String)

    created_at: Mapped[datetime.datetime] = Column(DateTime, default=datetime.datetime.now())

    def __str__(self):
        return f'{self.filepath}'


class Project(Base):
    __tablename__ = 'projects'

    id: Mapped[int] = Column(Integer, primary_key=True)

    title: Mapped[str] = Column(String, unique=True)
    content: Mapped[str] = Column(Text, default='base_content')

    image_id: Mapped[int] = Column(Integer, ForeignKey('images.id'), unique=True)
    image: Mapped["Image"] = relationship("Image", backref="project")

    created_at: Mapped[datetime.datetime] = Column(DateTime, default=datetime.datetime.now())

    def __str__(self):
        return f'Проект {self.title}'


class News(Base):
    __tablename__ = 'news'

    id: Mapped[int] = Column(Integer, primary_key=True)

    title: Mapped[str] = Column(String, unique=True)
    content: Mapped[str] = Column(Text, default='base_content')

    image_id: Mapped[int] = Column(Integer, ForeignKey('images.id'), unique=True)
    image: Mapped["Image"] = relationship("Image", backref="news")

    created_at: Mapped[datetime.datetime] = Column(DateTime, default=datetime.datetime.now())

    def __str__(self):
        return f'Новость "{self.title}"'


class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)

    name: Mapped[str] = Column(String(200), unique=True)
    description: Mapped[str] = Column(Text)
    price: Mapped[float] = Column(Float)

    is_active = Column(Boolean, default=True)

    def __str__(self):
        return self.name



