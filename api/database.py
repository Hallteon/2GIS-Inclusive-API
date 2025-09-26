import databases
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from settings import config_parameters

DATABASE_URL = (f"postgresql+asyncpg://{config_parameters.POSTGRES_DB_USERNAME}:{config_parameters.POSTGRES_DB_PASSWORD}@{config_parameters.POSTGRES_DB_HOST}:{config_parameters.POSTGRES_DB_PORT}/{config_parameters.POSTGRES_DB_NAME}")

database = databases.Database(DATABASE_URL)
Base = declarative_base()

engine = create_async_engine(DATABASE_URL, echo=True, future=True)
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session