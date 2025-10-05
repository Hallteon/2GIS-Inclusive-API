from __future__ import annotations

import requests
from typing import Optional, Tuple, Dict, Any

from settings import config_parameters


class DgisGeocoder:
    """
    Простой клиент для прямого геокодирования 2GIS:
    - geocode(address, ...) -> координаты (lat, lon)
    - resolve_city_id(city_name=...) или resolve_city_id(near=(lat, lon)) -> city_id

    near: кортеж (lat, lon). Во все запросы в 2GIS координаты передаём как "lon,lat".
    bbox: кортеж (lon1, lat1, lon2, lat2) — две противоположные вершины прямоугольника.
    radius: в метрах.
    """

    BASE_URL = "https://catalog.api.2gis.com/3.0/items/geocode"

    def __init__(self, timeout: float = 5.0, session: Optional[requests.Session] = None):
        self.api_key = config_parameters.GIS_API_KEY
        self.timeout = timeout
        self.http = session or requests.Session()

    def geocode(
        self,
        address: str,
        *,
        city_id: Optional[str] = None,
        near: Optional[Tuple[float, float]] = None,  # (lat, lon)
        radius: Optional[int] = None,
        bbox: Optional[Tuple[float, float, float, float]] = None,  # (lon1, lat1, lon2, lat2)
        polygon_wkt: Optional[str] = None,
        limit: int = 1,
    ) -> Optional[Dict[str, Any]]:
        """
        Возвращает словарь с ключами 'lat', 'lon' и 'raw' (сырой item из ответа) или None, если ничего не найдено.
        """
        params = {
            "q": address,
            "key": self.api_key,
            "fields": "items.point",  # гарантируем, что координаты будут в ответе
            "page_size": max(1, int(limit)),
        }

        if city_id:
            params["city_id"] = city_id

        if near:
            lat, lon = near
            if radius:
                params["point"] = f"{lon},{lat}"  # порядок 2GIS: lon,lat
                params["radius"] = int(radius)
            else:
                params["location"] = f"{lon},{lat}"
                params["sort"] = "distance"

        if bbox:
            lon1, lat1, lon2, lat2 = bbox
            params["point1"] = f"{lon1},{lat1}"
            params["point2"] = f"{lon2},{lat2}"

        if polygon_wkt:
            params["polygon"] = polygon_wkt

        resp = self.http.get(self.BASE_URL, params=params, timeout=self.timeout)
        resp.raise_for_status()
        data = resp.json()

        items = (data.get("result") or {}).get("items") or []
        for item in items:
            p = item.get("point")
            if p and "lat" in p and "lon" in p:
                return {"lat": p["lat"], "lon": p["lon"], "raw": item}
        return None

    def resolve_city_id(
        self,
        *,
        city_name: Optional[str] = None,
        near: Optional[Tuple[float, float]] = None,  # (lat, lon)
    ) -> Optional[str]:
        """
        Возвращает city_id (часть id ДО подчёркивания) для использования в geocode(..., city_id=...).
        """
        params = {
            "key": self.api_key,
            "type": "adm_div.city",
        }
        if city_name:
            params["q"] = city_name
        elif near:
            lat, lon = near
            params["lat"] = lat
            params["lon"] = lon
        else:
            raise ValueError("Нужно передать city_name или near=(lat, lon)")

        resp = self.http.get(self.BASE_URL, params=params, timeout=self.timeout)
        resp.raise_for_status()
        data = resp.json()
        items = (data.get("result") or {}).get("items") or []
        if not items:
            return None

        full_id = items[0].get("id") or ""
        return full_id.split("_", 1)[0] if "_" in full_id else full_id or None