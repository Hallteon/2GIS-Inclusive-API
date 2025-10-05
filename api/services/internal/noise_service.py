import json
import random
from typing import List


class NoiseService:
    async def get_noise_points(self, count: int) -> List[dict]:
        json_file_path = 'data/noise_analysis_results.json'

        try:
            with open(json_file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)

            noisy_points = [point for point in data if point.get('is_noisy') == True]

            if count >= len(noisy_points):
                return noisy_points

            return random.sample(noisy_points, count)

        except FileNotFoundError:
            print(f"Файл {json_file_path} не найден")
            return []

        except json.JSONDecodeError:
            print(f"Ошибка при чтении JSON файла {json_file_path}")
            return []

        except Exception as e:
            print(f"Произошла ошибка: {e}")
            return []