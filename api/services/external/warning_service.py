import requests

from typing import List, Set
from datetime import datetime

from api.utils.enums.warning_enum import EnvironmentWarning

from settings import config_parameters


class WarningService:
    async def get_weather_warnings(self, lat: float, lon: float) -> List[str]:
        warnings_set = set()
        api_key = config_parameters.VISUAL_CROSSING_API_KEY

        # Получаем данные за последние 7 дней и прогноз на 15 дней
        url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{lat},{lon}?key={api_key}&unitGroup=metric&lang=ru&include=days,hours,current"

        try:
            response = requests.get(url)
            response.raise_for_status()
            weather_data = response.json()

        except requests.exceptions.RequestException as e:
            print(f"Ошибка при запросе к API погоды: {e}")
            return list(warnings_set)

        # Анализ исторических данных за последние 7 дней для снега
        total_snow_last_week = await self._analyze_historical_snow(weather_data, warnings_set)
        if total_snow_last_week > 500:  # 500мм за неделю
            warnings_set.add(EnvironmentWarning.SNOW_WEATHER.value)

        # Анализ прогноза на ближайшие 10 часов
        await self._analyze_10_hour_forecast(weather_data, warnings_set)

        return list(warnings_set)

    async def _analyze_historical_snow(self, weather_data: dict, warnings_set: Set[str]) -> float:
        """Анализирует снег за последние 7 дней"""
        total_snow = 0.0
        today = datetime.now().date()

        for day_data in weather_data.get('days', []):
            # Получаем дату из timestamp
            day_date = datetime.fromtimestamp(day_data['datetimeEpoch']).date()
            days_diff = (today - day_date).days

            # Берем данные только за последние 7 дней (включая сегодня)
            if 0 <= days_diff <= 7:
                snow_depth = day_data.get('snowdepth', 0)  # Текущий снежный покров
                snow = day_data.get('snow', 0)  # Выпавший снег
                precip = day_data.get('precip', 0)  # Осадки

                # Если есть данные о снежном покрове и он больше 50мм
                if snow_depth > 50:
                    warnings_set.add(EnvironmentWarning.SNOW_WEATHER.value)

                # Суммируем все осадки, которые могли быть снегом
                # В холодные дни предполагаем, что осадки были снежными
                temp_max = day_data.get('tempmax', 0)
                if temp_max <= 2:  # Если максимальная температура <= 2°C, считаем что осадки были снегом
                    total_snow += precip
                else:
                    total_snow += snow  # Используем прямое значение снега если есть

        return total_snow

    async def _analyze_10_hour_forecast(self, weather_data: dict, warnings_set: Set[str]):
        """Анализирует прогноз на ближайшие 10 часов"""
        current_hour = datetime.now().hour
        hours_analyzed = 0

        # Ищем сегодняшний день и анализируем часы
        for day_data in weather_data.get('days', []):
            day_date = datetime.fromtimestamp(day_data['datetimeEpoch']).date()
            today = datetime.now().date()

            if day_date == today:
                hours = day_data.get('hours', [])

                for hour_data in hours:
                    hour_time = datetime.fromtimestamp(hour_data['datetimeEpoch'])

                    # Анализируем только будущие часы + текущий
                    if hour_time.hour >= current_hour and hours_analyzed < 10:
                        await self._analyze_hour_conditions(hour_data, warnings_set)
                        hours_analyzed += 1

                break

        # Если сегодняшних часов недостаточно, берем из завтрашнего дня
        if hours_analyzed < 10:
            for day_data in weather_data.get('days', []):
                day_date = datetime.fromtimestamp(day_data['datetimeEpoch']).date()
                today = datetime.now().date()

                if day_date > today:  # Завтрашний день
                    hours = day_data.get('hours', [])

                    for hour_data in hours:
                        if hours_analyzed < 10:
                            await self._analyze_hour_conditions(hour_data, warnings_set)
                            hours_analyzed += 1
                    break

    async def _analyze_hour_conditions(self, hour_data: dict, warnings_set: Set[str]):
        """Анализирует погодные условия для конкретного часа"""
        temp = hour_data.get('temp', 0)
        dew_point = hour_data.get('dew', temp)
        conditions = hour_data.get('conditions', '').lower()
        precip_type = hour_data.get('preciptype', [])
        precip = hour_data.get('precip', 0)

        # Проверка на дождь
        if ('rain' in conditions or
                (precip_type and any(p in ['rain'] for p in precip_type))):
            warnings_set.add(EnvironmentWarning.RAIN_WEATHER.value)

        # Проверка на снег (текущий и прогнозируемый)
        if ('snow' in conditions or
                (precip_type and any(p in ['snow'] for p in precip_type)) or
                precip > 0 and temp <= 1):  # Осадки при температуре <= 1°C считаем снегом
            warnings_set.add(EnvironmentWarning.SNOW_WEATHER.value)

        # Проверка на гололёд
        await self._check_ice_conditions(hour_data, warnings_set)

    async def _check_ice_conditions(self, hour_data: dict, warnings_set: Set[str]):
        """Проверяет условия для гололёда"""
        temp = hour_data.get('temp', 0)
        dew_point = hour_data.get('dew', temp)
        conditions = hour_data.get('conditions', '').lower()
        precip_type = hour_data.get('preciptype', [])
        humidity = hour_data.get('humidity', 0)

        has_precipitation = ('rain' in conditions or 'snow' in conditions or
                             (precip_type and len(precip_type) > 0))

        # Способ 1: По температуре и точке росы
        temp_dew_close = abs(temp - dew_point) <= 1
        freezing_conditions = -2 <= temp <= 1 and temp_dew_close

        # Способ 2: По типу осадков (ледяной дождь, мокрый снег)
        freezing_precip = any(ft in str(precip_type).lower() for ft in ['freezing', 'sleet', 'ice'])

        # Способ 3: По влажности и температуре (для гололеда без осадков)
        high_humidity_freeze = temp <= 0 and humidity > 85

        if (freezing_precip or freezing_conditions or
                (high_humidity_freeze and has_precipitation)):
            warnings_set.add(EnvironmentWarning.ICE_WEATHER.value)