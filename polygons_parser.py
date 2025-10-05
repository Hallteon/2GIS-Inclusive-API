# events_importer.py
from __future__ import annotations

import asyncio
import csv
import logging
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple, Union

import httpx


class EventsCsvImporter:
    EVENTS_CREATE = "/events/create"
    CATEGORY_GET = "/events/categories/get_by_name"
    CATEGORY_CREATE = "/events/categories/create"

    def __init__(
            self,
            base_url: str = "https://2gis-bratskiy.ru",
            *,
            category_column: Optional[str] = None,
            create_missing_categories: bool = True,
            concurrency: int = 5,
            timeout: float = 20.0,
            retries: int = 3,
            backoff_base: float = 0.6,
            verify_ssl: bool = True,
            headers: Optional[Dict[str, str]] = None,
            dry_run: bool = False,
            logger: Optional[logging.Logger] = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.category_column = category_column
        self.create_missing_categories = create_missing_categories
        self.concurrency = max(1, concurrency)
        self.timeout = timeout
        self.retries = max(0, retries)
        self.backoff_base = max(0.05, backoff_base)
        self.verify_ssl = verify_ssl
        self.headers = headers or {"Accept": "application/json", "Content-Type": "application/json"}
        self.dry_run = dry_run

        self._client: Optional[httpx.AsyncClient] = None
        self._sem = asyncio.Semaphore(self.concurrency)
        self._category_cache: Dict[str, int] = {}
        self._category_create_locks: Dict[str, asyncio.Lock] = {}

        self.log = logger or logging.getLogger(self.__class__.__name__)

    async def __aenter__(self) -> "EventsCsvImporter":
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout,
            headers=self.headers,
            verify=self.verify_ssl,
        )
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None

    # --------------------------
    # Публичные методы
    # --------------------------
    async def import_csv(
            self,
            file_path: Union[str, Path],
            *,
            encoding: str = "utf-8-sig",
            delimiter: Optional[str] = None,
            limit: Optional[int] = None,
            row_id_field: str = "uuid",
    ) -> Dict[str, Any]:
        """
        Импортирует CSV построчно. Возвращает сводку.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"CSV файл не найден: {path}")

        with path.open("r", encoding=encoding, newline="") as f:
            sample = f.read(8192)
            f.seek(0)
            if delimiter is None:
                delimiter = self._detect_delimiter(sample)
                self.log.info("Определен разделитель CSV: %r", delimiter)

            reader = csv.DictReader(f, delimiter=delimiter)
            total = 0
            tasks = []
            for row in reader:
                if limit is not None and total >= limit:
                    break
                total += 1
                tasks.append(self._process_row(row, row_num=total, row_id=row.get(row_id_field)))

        results = await self._gather_limited(tasks)
        success = [r for r in results if r["ok"]]
        failed = [r for r in results if not r["ok"]]

        summary = {
            "total_rows": len(results),
            "success": len(success),
            "failed": len(failed),
            "fail_examples": failed[:5],
        }

        self.log.info("Импорт завершен: %s", summary)
        return summary

    # --------------------------
    # Внутренние методы
    # --------------------------
    async def _process_row(self, row: Dict[str, Any], *, row_num: int, row_id: Optional[str]) -> Dict[str, Any]:
        """
        Обрабатывает одну строку: собирает payload, вызывает API, обрабатывает ошибки.
        """
        row_tag = f"row#{row_num}"
        if row_id:
            row_tag += f"({row_id})"

        try:
            payload = await self._build_payload(row)
            self._scrub_empty_strings(payload)

            if self.dry_run:
                self.log.info("%s DRY-RUN payload: %s", row_tag, payload)
                return {"ok": True, "row": row_num, "row_id": row_id, "event_id": None, "dry_run": True}

            event_id = await self._create_event(payload)
            self.log.info("%s Создано событие id=%s", row_tag, event_id)
            return {"ok": True, "row": row_num, "row_id": row_id, "event_id": event_id}

        except Exception as e:
            self.log.error("%s Ошибка: %s", row_tag, e)
            return {"ok": False, "row": row_num, "row_id": row_id, "error": str(e)}

    async def _build_payload(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """
        Преобразует строку CSV в JSON для EventCreateScheme.
        """
        payload: Dict[str, Any] = {
            "address": self._clean_str(row.get("address")),
            "comment": self._clean_str(row.get("comment")),
            "work": self._clean_str(row.get("work")),
            "worker": self._clean_str(row.get("worker")),
            "start_datetime": self._to_iso_or_none(row.get("start_date")),
            "end_datetime": self._to_iso_or_none(row.get("end_date")),
            "geom": self._parse_wkt_to_latlon_list(row.get("geom")),
        }

        # Категория (опционально)
        if self.category_column:
            category_name = self._clean_str(row.get(self.category_column))
            if category_name:
                category_id = await self._get_or_create_category(category_name)
                if category_id is not None:
                    payload["category_id"] = category_id
                else:
                    self.log.warning("Не удалось получить/создать категорию '%s'", category_name)

        return payload

    async def _get_or_create_category(self, name: str) -> Optional[int]:
        """
        Возвращает id категории по имени. Если не найдена и разрешено — создает.
        """

        if name in self._category_cache:
            return self._category_cache[name]

        if name not in self._category_create_locks:
            self._category_create_locks[name] = asyncio.Lock()

        async with self._category_create_locks[name]:
            if name in self._category_cache:
                return self._category_cache[name]

            category_id = await self._get_category_by_name(name)
            if category_id is not None:
                self._category_cache[name] = category_id
                return category_id

            if self.create_missing_categories:
                category_id = await self._create_category(name)
                if category_id is not None:
                    self._category_cache[name] = category_id
                    return category_id

            return None

    async def _get_category_by_name(self, name: str) -> Optional[int]:
        """
        Ищет категорию по имени через GET /events/get_by_name.
        Возвращает id категории или None если не найдена.
        """
        try:
            r = await self._request(
                "GET", self.CATEGORY_GET,
                params={"name": name},
                expected_statuses=(200, 404)
            )

            if r.status_code == 200:
                data = r.json()
                self.log.debug("Ответ от categories/get_by_name для '%s': %s", name, data)

                if isinstance(data, dict) and "id" in data:
                    category_id = data["id"]
                    if isinstance(category_id, int):
                        self.log.info("Найдена категория '%s' → id=%s", name, category_id)
                        return category_id
                self.log.warning("Некорректный формат ответа для категории '%s': %s", name, data)

            elif r.status_code == 404:
                self.log.info("Категория '%s' не найдена", name)
                return None

        except Exception as e:
            self.log.error("Ошибка при поиске категории '%s': %s", name, e)

        return None

    async def _create_category(self, name: str) -> Optional[int]:
        """
        Создает новую категорию через POST /events/categories/create.
        Возвращает id созданной категории или None при ошибке.
        """
        try:
            r = await self._request(
                "POST", self.CATEGORY_CREATE,
                json={"name": name},
                expected_statuses=(200, 201)
            )

            category_id = r.json()
            if isinstance(category_id, int):
                self.log.info("Создана категория '%s' → id=%s", name, category_id)
                return category_id
            else:
                self.log.error("Некорректный ответ при создании категории '%s': %s", name, category_id)

        except Exception as e:
            self.log.error("Ошибка создания категории '%s': %s", name, e)

        return None

    async def _create_event(self, payload: Dict[str, Any]) -> int:
        """
        POST /events/create → int (id события).
        """
        r = await self._request("POST", self.EVENTS_CREATE, json=payload)

        try:
            event_id = r.json()
        except Exception as e:
            self.log.error("Ошибка парсинга ответа: %s, текст ответа: %s", e, r.text)
            raise RuntimeError(f"Некорректный ответ API при создании события: {r.status_code}")

        if not isinstance(event_id, int):
            raise RuntimeError(f"Ожидался int (id), получено: {event_id!r}")
        return event_id

    async def _request(
            self,
            method: str,
            url: str,
            *,
            params: Optional[Dict[str, Any]] = None,
            json: Optional[Dict[str, Any]] = None,
            expected_statuses: Tuple[int, ...] = (200,),
    ) -> httpx.Response:
        """
        HTTP-запрос с ретраями и бэкоффом.
        """
        if not self._client:
            raise RuntimeError("HTTP клиент не инициализирован. Используй 'async with EventsCsvImporter(...)'.")

        for attempt in range(self.retries + 1):
            try:
                async with self._sem:
                    r = await self._client.request(method, url, params=params, json=json)

                if r.status_code in expected_statuses:
                    return r

                if 400 <= r.status_code < 500:
                    raise httpx.HTTPStatusError(
                        f"{method} {url} → {r.status_code}: {r.text}", request=None, response=r
                    )

                self.log.warning("Сервер вернул %s. Попытка %s/%s", r.status_code, attempt + 1, self.retries + 1)

            except (httpx.ConnectError, httpx.ReadTimeout, httpx.RemoteProtocolError, httpx.HTTPStatusError) as e:
                if attempt >= self.retries:
                    raise
                sleep_for = self.backoff_base * (2 ** attempt)
                self.log.warning("HTTP ошибка '%s'. Ретрай через %.2fs (%s/%s)", e, sleep_for, attempt + 1,
                                 self.retries + 1)
                await asyncio.sleep(sleep_for)

        raise RuntimeError(f"{method} {url}: не удалось получить успешный ответ после {self.retries + 1} попыток.")

    # --------------------------
    # Парсинг и утилиты
    # --------------------------
    @staticmethod
    def _detect_delimiter(sample: str) -> str:
        candidates = ["\t", ";", ","]
        counts = {c: sample.count(c) for c in candidates}
        delim = max(counts, key=counts.get)
        return delim

    @staticmethod
    def _clean_str(value: Any) -> Optional[str]:
        if value is None:
            return None
        s = str(value).strip()
        return s if s != "" else None

    @staticmethod
    def _to_iso_or_none(value: Any) -> Optional[str]:
        if value is None:
            return None
        s = str(value).strip()
        if s == "":
            return None
        # Преобразуем в ISO формат если нужно
        if " " in s and "T" not in s:
            s = s.replace(" ", "T")
        return s

    @staticmethod
    def _parse_wkt_to_latlon_list(wkt: Any) -> Optional[List[Dict[str, float]]]:
        """
        Преобразует WKT в список [{'lat': float, 'lon': float}, ...].
        """
        if not wkt:
            return None
        s = str(wkt).strip()
        if s == "":
            return None

        points: List[Dict[str, float]] = []

        try:
            coord_pattern = r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?"
            coord_pairs = re.findall(rf"({coord_pattern}\s+{coord_pattern})", s)

            for pair in coord_pairs:
                coords = re.findall(coord_pattern, pair)
                if len(coords) >= 2:
                    lon = float(coords[0])
                    lat = float(coords[1])
                    points.append({"lat": lat, "lon": lon})

        except Exception as e:
            logging.debug("Ошибка парсинга WKT %r: %s", wkt, e)
            return None

        return points or None

    @staticmethod
    def _scrub_empty_strings(payload: Dict[str, Any]) -> None:
        """
        Превращает пустые строки в None.
        """
        for k, v in list(payload.items()):
            if isinstance(v, str) and v.strip() == "":
                payload[k] = None

    async def _gather_limited(self, coroutines: List[asyncio.Future]) -> List[Any]:
        """
        Аккуратно ждет выполнения набора задач.
        """
        results: List[Any] = []
        for coro in asyncio.as_completed(coroutines):
            try:
                res = await coro
            except Exception as e:
                results.append({"ok": False, "error": str(e)})
            else:
                results.append(res)
        return results


# Синхронная обертка
def import_events_from_csv(
        path: Union[str, Path],
        *,
        base_url: str = "https://2gis-bratskiy.ru",
        category_column: Optional[str] = None,
        create_missing_categories: bool = True,
        concurrency: int = 5,
        timeout: float = 20.0,
        retries: int = 3,
        backoff_base: float = 0.6,
        verify_ssl: bool = True,
        headers: Optional[Dict[str, str]] = None,
        dry_run: bool = False,
        encoding: str = "utf-8-sig",
        delimiter: Optional[str] = None,
        limit: Optional[int] = None,
        row_id_field: str = "uuid",
) -> Dict[str, Any]:
    """
    Синхронная обертка для импорта событий из CSV.
    """

    async def _run():
        async with EventsCsvImporter(
                base_url=base_url,
                category_column=category_column,
                create_missing_categories=create_missing_categories,
                concurrency=concurrency,
                timeout=timeout,
                retries=retries,
                backoff_base=backoff_base,
                verify_ssl=verify_ssl,
                headers=headers,
                dry_run=dry_run,
        ) as importer:
            return await importer.import_csv(
                path, encoding=encoding, delimiter=delimiter, limit=limit, row_id_field=row_id_field
            )

    return asyncio.run(_run())


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    print("=== DRY RUN ===")
    summary = import_events_from_csv(
        "data/events.csv",
        base_url="https://2gis-bratskiy.ru",
        category_column="event_type_name",
        create_missing_categories=True,
        concurrency=2,
        dry_run=True,  # Только просмотр payload
        encoding="utf-8-sig",
        limit=3,  # Только первые 3 строки для теста
        row_id_field="uuid"
    )

    print("Dry run summary:", summary)

    # Спросим пользователя хочет ли он продолжить с реальным импортом
    if summary["failed"] == 0:
        response = input("\nDry run успешен. Продолжить с реальным импортом? (y/n): ")
        if response.lower() in ['y', 'yes', 'да']:
            print("\n=== REAL IMPORT ===")
            summary = import_events_from_csv(
                "data/events.csv",
                base_url="https://2gis-bratskiy.ru",
                category_column="event_type_name",
                create_missing_categories=True,
                concurrency=2,
                dry_run=False,  # Реальный импорт
                encoding="utf-8-sig",
                limit=500,
                row_id_field="uuid"
            )
            print("Real import summary:", summary)
        else:
            print("Импорт отменен.")
    else:
        print("Dry run завершился с ошибками. Проверьте данные и настройки.")