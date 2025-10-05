import json
import csv
from collections import defaultdict
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import re

from api.services.external.geocoder_service import DgisGeocoder


@dataclass
class NoiseAnalysisResult:
    """Результат анализа шума для одного адреса"""
    lat: float
    lon: float
    address: str
    is_noisy: bool
    complaint_frequency: str  # "низкая", "средняя", "высокая"
    total_complaints: int
    noisy_complaints: int
    noise_sources: List[str]
    last_check_date: str


class NoiseAnalysisService:
    """Сервис для анализа шумовых обращений"""

    def __init__(self, geocoder: DgisGeocoder):
        self.geocoder = geocoder
        self.noise_keywords = {
            'превышения нормативов': True,
            'выявлены превышения': True,
            'не выявлены': False,
            'превышения не выявлены': False,
            'не производились': False
        }

        self.frequency_thresholds = {
            'низкая': 1,
            'средняя': 3,
            'высокая': 5
        }

    def parse_csv_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Парсинг CSV файла с обращениями по шуму"""
        records = []

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                # Читаем все строки
                lines = file.readlines()
                print(f"Всего строк в файле: {len(lines)}")

                # Пропускаем первые две строки с заголовками
                data_lines = lines[2:]  # пропускаем строки 0 и 1
                print(f"Строк с данными: {len(data_lines)}")

                # Определяем имена полей из первой строки заголовков
                fieldnames_line = lines[0].strip().split(';')
                fieldnames = [field.strip('"') for field in fieldnames_line]
                print(f"Поля CSV: {fieldnames}")

                for line_num, line in enumerate(data_lines, start=3):
                    try:
                        if not line.strip():
                            continue

                        # Разбиваем строку по точкам с запятой
                        row_data = line.strip().split(';')

                        # Создаем словарь из данных
                        row_dict = {}
                        for i, field in enumerate(fieldnames):
                            if i < len(row_data):
                                # Убираем кавычки из значений
                                value = row_data[i].strip('"').strip()
                                row_dict[field] = value
                            else:
                                row_dict[field] = ""

                        address = row_dict.get('Location', '')
                        if not address:
                            print(f"Пропущена строка {line_num}: отсутствует адрес")
                            continue

                        record = {
                            'id': row_dict.get('ID', '').strip(),
                            'date': row_dict.get('Date', '').strip(),
                            'address': address,
                            'district': row_dict.get('District', '').strip(),
                            'adm_area': row_dict.get('AdmArea', '').strip(),
                            'noise_category': row_dict.get('NoiseCategory', '').strip(),
                            'results': row_dict.get('Results', '').strip(),
                            'longitude': self._parse_coordinate(row_dict.get('Longitude_WGS84', '')),
                            'latitude': self._parse_coordinate(row_dict.get('Latitude_WGS84', ''))
                        }

                        # Отладочная информация для первых нескольких записей
                        if len(records) < 5:
                            print(f"Пример записи {line_num}:")
                            print(f"  Адрес: {address}")
                            print(f"  Координаты: {record['latitude']}, {record['longitude']}")
                            print(f"  Дата: {record['date']}")
                            print(f"  Категория: {record['noise_category']}")

                        records.append(record)

                    except Exception as e:
                        print(f"Ошибка обработки строки {line_num}: {e}")
                        print(f"Содержание строки: {line}")
                        continue

        except Exception as e:
            print(f"Ошибка чтения файла {file_path}: {e}")
            import traceback
            traceback.print_exc()

        print(f"Успешно обработано {len(records)} записей")
        return records

    def _parse_coordinate(self, coord_str: str) -> Optional[float]:
        """Парсинг координат из строки"""
        if not coord_str:
            return None
        try:
            # Убираем кавычки и лишние пробелы
            clean_str = str(coord_str).replace('"', '').strip()
            if clean_str:
                return float(clean_str)
            return None
        except (ValueError, TypeError) as e:
            print(f"Ошибка парсинга координаты '{coord_str}': {e}")
            return None

    def geocode_address(self, address: str, city: str = "Москва") -> Optional[Tuple[float, float]]:
        """Геокодирование адреса в координаты"""
        try:
            # Добавляем город к адресу для лучшего геокодирования
            full_address = f"{city}, {address}"
            print(f"Геокодирование адреса: {full_address}")

            result = self.geocoder.geocode(full_address)

            if result:
                print(f"Успешно геокодировано: {result['lat']}, {result['lon']}")
                return result['lat'], result['lon']
            else:
                print(f"Не удалось геокодировать адрес: {full_address}")
                return None

        except Exception as e:
            print(f"Ошибка геокодирования адреса {address}: {e}")
            return None

    def analyze_noise_result(self, results_text: str) -> bool:
        """Анализ текста результатов на наличие шума"""
        if not results_text:
            return False

        results_lower = results_text.lower()

        # Проверяем ключевые фразы в порядке приоритета
        for phrase, is_noisy in self.noise_keywords.items():
            if phrase in results_lower:
                return is_noisy

        # Если явных указаний нет, считаем что шум есть (осторожный подход)
        return True

    def extract_noise_sources(self, noise_category: str, results_text: str) -> List[str]:
        """Извлечение источников шума из категории и результатов"""
        sources = []

        # Источники из категории шума
        if noise_category and noise_category != "None" and noise_category != "null":
            # Очищаем категорию от лишних символов
            category_clean = re.sub(r'[\[\]]', '', noise_category)
            if category_clean and category_clean != "None":
                sources.append(category_clean)

        # Дополнительные источники из текста результатов
        if results_text:
            results_lower = results_text.lower()
            common_sources = [
                'автотранспорт', 'строительные работы', 'вентиляционные системы',
                'генераторная установка', 'промышленное предприятие', 'железнодорожный транспорт',
                'дорожно-ремонтные работы', 'погрузочно-разгрузочные работы', 'летнее кафе',
                'автомойка', 'музыка', 'кафе', 'ресторан', 'клуб'
            ]

            for source in common_sources:
                if source in results_lower:
                    sources.append(source)

        # Убираем дубликаты
        return list(set(sources))

    def calculate_complaint_frequency(self, complaint_count: int) -> str:
        """Определение частоты обращений"""
        if complaint_count >= self.frequency_thresholds['высокая']:
            return 'высокая'
        elif complaint_count >= self.frequency_thresholds['средняя']:
            return 'средняя'
        else:
            return 'низкая'

    def analyze_complaints(self, records: List[Dict[str, Any]]) -> List[NoiseAnalysisResult]:
        """Анализ всех обращений и группировка по адресам"""
        # Группируем обращения по адресам
        address_groups = defaultdict(list)

        for record in records:
            address = record['address']
            address_groups[address].append(record)

        results = []

        print(f"Найдено {len(address_groups)} уникальных адресов")

        for address, complaints in address_groups.items():
            print(f"Анализ адреса: {address}, обращений: {len(complaints)}")

            # Сортируем по дате (последние сначала)
            complaints_sorted = sorted(
                complaints,
                key=lambda x: x['date'],
                reverse=True
            )

            # Берем координаты из первой записи или геокодируем
            lat, lon = None, None
            if complaints_sorted[0]['latitude'] and complaints_sorted[0]['longitude']:
                lat = complaints_sorted[0]['latitude']
                lon = complaints_sorted[0]['longitude']
                print(f"Использованы координаты из CSV: {lat}, {lon}")
            else:
                # Геокодируем адрес
                print(f"Геокодирование адреса: {address}")
                coords = self.geocode_address(address)
                if coords:
                    lat, lon = coords
                    print(f"Геокодированные координаты: {lat}, {lon}")

            if not lat or not lon:
                print(f"Не удалось получить координаты для адреса: {address}")
                continue

            # Анализируем результаты обращений
            total_complaints = len(complaints)
            noisy_complaints = 0
            all_noise_sources = []

            for complaint in complaints:
                is_noisy = self.analyze_noise_result(complaint['results'])
                if is_noisy:
                    noisy_complaints += 1

                # Собираем источники шума
                sources = self.extract_noise_sources(
                    complaint['noise_category'],
                    complaint['results']
                )
                all_noise_sources.extend(sources)

            # Определяем общий уровень шума
            # Если более 50% обращений подтверждают шум - считаем адрес шумным
            noise_ratio = noisy_complaints / total_complaints if total_complaints > 0 else 0
            is_address_noisy = noise_ratio > 0.5

            print(
                f"Адрес {address}: шумных обращений {noisy_complaints}/{total_complaints} ({(noise_ratio * 100):.1f}%)")

            # Уникальные источники шума
            unique_sources = list(set(all_noise_sources))

            # Частота обращений
            frequency = self.calculate_complaint_frequency(total_complaints)

            result = NoiseAnalysisResult(
                lat=lat,
                lon=lon,
                address=address,
                is_noisy=is_address_noisy,
                complaint_frequency=frequency,
                total_complaints=total_complaints,
                noisy_complaints=noisy_complaints,
                noise_sources=unique_sources,
                last_check_date=complaints_sorted[0]['date']
            )

            results.append(result)

        return results

    def save_to_json(self, results: List[NoiseAnalysisResult], output_file: str):
        """Сохранение результатов в JSON файл"""
        output_data = []

        for result in results:
            result_dict = {
                'latitude': result.lat,
                'longitude': result.lon,
                'address': result.address,
                'is_noisy': result.is_noisy,
                'complaint_frequency': result.complaint_frequency,
                'total_complaints': result.total_complaints,
                'noisy_complaints': result.noisy_complaints,
                'noise_sources': result.noise_sources,
                'last_check_date': result.last_check_date,
                'noise_ratio': round(result.noisy_complaints / result.total_complaints, 2)
            }
            output_data.append(result_dict)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)

        print(f"Сохранено {len(output_data)} записей в {output_file}")

    def process_noise_data(self, csv_file_path: str, output_json_path: str):
        """Полный процесс обработки данных о шуме"""
        print("=" * 50)
        print("Начало обработки данных о шуме")
        print("=" * 50)

        print("Чтение CSV файла...")
        records = self.parse_csv_file(csv_file_path)

        if not records:
            print("ОШИБКА: Не удалось прочитать ни одной записи из CSV файла")
            print("Попробуем альтернативный метод чтения...")
            records = self._parse_csv_alternative(csv_file_path)

        if not records:
            print("Не удалось прочитать данные. Проверьте файл.")
            return

        print(f"Прочитано {len(records)} записей")

        print("Анализ обращений по шуму...")
        analysis_results = self.analyze_complaints(records)
        print(f"Проанализировано {len(analysis_results)} уникальных адресов")

        print("Сохранение результатов в JSON...")
        self.save_to_json(analysis_results, output_json_path)
        print(f"Результаты сохранены в {output_json_path}")

        # Статистика
        if analysis_results:
            noisy_count = sum(1 for r in analysis_results if r.is_noisy)
            print(f"\nСтатистика:")
            print(
                f"Шумные адреса: {noisy_count}/{len(analysis_results)} ({(noisy_count / len(analysis_results) * 100):.1f}%)")
            print(
                f"Тихие адреса: {len(analysis_results) - noisy_count}/{len(analysis_results)} ({((len(analysis_results) - noisy_count) / len(analysis_results) * 100):.1f}%)")

            # Распределение по частоте обращений
            freq_dist = defaultdict(int)
            for result in analysis_results:
                freq_dist[result.complaint_frequency] += 1

            print(f"\nРаспределение по частоте обращений:")
            for freq, count in freq_dist.items():
                print(f"  {freq}: {count} адресов")
        else:
            print("Нет данных для статистики")

    def _parse_csv_alternative(self, file_path: str) -> List[Dict[str, Any]]:
        """Альтернативный метод парсинга CSV"""
        records = []
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.reader(file, delimiter=';')

                # Читаем заголовки
                headers1 = next(reader)  # первая строка заголовков
                headers2 = next(reader)  # вторая строка заголовков

                # Используем первую строку как имена полей
                fieldnames = [h.strip('"') for h in headers1]
                print(f"Альтернативные поля: {fieldnames}")

                for row_num, row in enumerate(reader, start=3):
                    if not row or len(row) < 8:
                        continue

                    try:
                        # Создаем словарь
                        row_dict = {}
                        for i, field in enumerate(fieldnames):
                            if i < len(row):
                                value = row[i].strip('"').strip()
                                row_dict[field] = value
                            else:
                                row_dict[field] = ""

                        address = row_dict.get('Location', '')
                        if address:
                            record = {
                                'id': row_dict.get('ID', ''),
                                'date': row_dict.get('Date', ''),
                                'address': address,
                                'district': row_dict.get('District', ''),
                                'adm_area': row_dict.get('AdmArea', ''),
                                'noise_category': row_dict.get('NoiseCategory', ''),
                                'results': row_dict.get('Results', ''),
                                'longitude': self._parse_coordinate(row_dict.get('Longitude_WGS84', '')),
                                'latitude': self._parse_coordinate(row_dict.get('Latitude_WGS84', ''))
                            }
                            records.append(record)

                    except Exception as e:
                        print(f"Ошибка в альтернативном парсинге строки {row_num}: {e}")
                        continue

        except Exception as e:
            print(f"Ошибка альтернативного чтения: {e}")

        print(f"Альтернативным методом обработано {len(records)} записей")
        return records


# Пример использования
if __name__ == "__main__":
    try:
        # Инициализация геокодера
        geocoder = DgisGeocoder()

        # Создание сервиса анализа
        noise_service = NoiseAnalysisService(geocoder)

        # Обработка данных
        noise_service.process_noise_data(
            csv_file_path="data/noise.csv",
            output_json_path="data/noise_analysis_results.json"
        )

        input("Нажмите Enter для выхода...")

    except Exception as e:
        print(f"Критическая ошибка: {e}")
        import traceback

        traceback.print_exc()
        input("Нажмите Enter для выхода...")