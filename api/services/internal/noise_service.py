import json

from typing import List

from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.database import get_async_session


class NoiseService:
    async def get_noise_points(self) -> List[dict]:
        json_file_path = "data/noise_analysis_results.json"

        try:
            with open(json_file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)

            noisy_points = [point for point in data if point.get('is_noisy') == True]

            return noisy_points

        except FileNotFoundError:
            print(f"Файл {json_file_path} не найден")
            return []

        except json.JSONDecodeError:
            print(f"Ошибка при чтении JSON файла {json_file_path}")
            return []

        except Exception as e:
            print(f"Произошла ошибка: {e}")
            return []