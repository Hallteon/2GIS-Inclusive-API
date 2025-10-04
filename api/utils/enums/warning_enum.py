from enum import Enum


class EnvironmentWarning(Enum):
    RAIN_WEATHER = 'дождь'
    SNOW_WEATHER = 'снег'
    ICE_WEATHER = 'гололёд'
    HIGH_TRAFFIC = 'час пик'