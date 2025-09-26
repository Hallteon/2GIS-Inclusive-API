from typing import Optional

from pydantic import BaseModel, Field
from fastapi import UploadFile, File


class ImageDescribeScheme(BaseModel):
    description: Optional[str] = File(None, description='Описание изображения')

