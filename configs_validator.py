from typing import Union, List
from pydantic import BaseModel


class AdminConfigsModel(BaseModel):
    ADMIN_USERNAME: Union[str]
    ADMIN_HASHED_PASSWORD: Union[str]


class PostgresDataBaseConfigsModel(BaseModel):
    POSTGRES_DB_USERNAME: Union[str]
    POSTGRES_DB_PASSWORD: Union[str]
    POSTGRES_DB_HOST: Union[str]
    POSTGRES_DB_PORT: Union[str]
    POSTGRES_DB_NAME: Union[str]


class APIConfigsModel(BaseModel):
    API_HOST: Union[str]
    API_PORT: Union[int]
    API_URL: Union[str, None] = None

    STATIC_DIR: Union[str]
    SECRET_KEY: Union[str]
    MEDIA_DIR: Union[str]

    ORGANIZATION_IMAGE_DIR: Union[str]

    DOMAIN: Union[str]

    IS_PROD: Union[bool]


class LLMConfigsModel(BaseModel):
    OPENROUTER_API_KEY: Union[str]


class WeatherConfigsModel(BaseModel):
    VISUAL_CROSSING_API_KEY: Union[str]


class ConfigsValidator(APIConfigsModel, AdminConfigsModel, WeatherConfigsModel,
                       PostgresDataBaseConfigsModel, LLMConfigsModel):
    pass