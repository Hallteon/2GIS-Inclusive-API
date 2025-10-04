import os

from fastapi import UploadFile


class ImageUploadService:
    async def save_image(self, image: UploadFile, image_filepath: str) -> str:
        os.makedirs(os.path.dirname(image_filepath), exist_ok=True)

        with open(image_filepath, "wb+") as file_object:
            file_object.write(image.file.read())

        return image_filepath

    async def delete_image(self, image_filepath: str) -> bool:
        os.remove(image_filepath)

        return True


