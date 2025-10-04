from typing import Optional

from pydantic import BaseModel
from fastapi import File


class ImageDescribeScheme(BaseModel):
    description: Optional[str] = File(None, description='Описание изображения')

