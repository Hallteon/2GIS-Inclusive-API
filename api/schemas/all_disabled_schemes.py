from pydantic import BaseModel, Field


class WarningGetScheme(BaseModel):
    latitude: float = Field(..., description='Широта')
    longitude: float = Field(..., description='Долгота')