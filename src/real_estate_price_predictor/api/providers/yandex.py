from typing import Any

import httpx

from ...config import YANDEX_API_KEY


class YandexAPIError(Exception):
    """Ошибка взаимодействия с Yandex Maps API."""


class YandexGeocoder:
    BASE_URL = (
        "https://geocode-maps.yandex.ru/v1/"
    )

    def __init__(
            self,
            api_key: str | None = YANDEX_API_KEY,
    ) -> None:
        self.api_key = api_key

    async def geocode_uri(
            self,
            uri: str,
    ) -> dict[str, Any]:
        if not self.api_key:
            raise YandexAPIError(
                "YANDEX_GEOCODER_API_KEY is not configured."
            )

        params = {
            "apikey": self.api_key,
            "uri": uri,
            "format": "json",
            "lang": "ru_RU",
        }

        try:
            async with httpx.AsyncClient(
                    timeout=10.0,
            ) as client:
                response = await client.get(
                    self.BASE_URL,
                    params=params,
                )
        except httpx.HTTPError as exc:
            raise YandexAPIError(
                "Failed to connect to Yandex Geocoder."
            ) from exc

        if response.status_code == 403:
            raise YandexAPIError(
                "Yandex Geocoder rejected the API key."
            )

        if response.status_code == 429:
            raise YandexAPIError(
                "Yandex Geocoder rate limit exceeded."
            )

        if response.is_error:
            raise YandexAPIError(
                f"Yandex Geocoder returned "
                f"HTTP {response.status_code}."
            )

        try:
            data = response.json()
        except ValueError as exc:
            raise YandexAPIError(
                "Yandex Geocoder returned invalid JSON."
            ) from exc

        return data

    async def get_coordinates_by_uri(
            self,
            uri: str,
    ) -> tuple[float, float]:
        data = await self.geocode_uri(uri)

        try:
            members = (
                data["response"]
                ["GeoObjectCollection"]
                ["featureMember"]
            )
        except KeyError as exc:
            raise YandexAPIError(
                "Unexpected Yandex Geocoder response."
            ) from exc

        if not members:
            raise YandexAPIError(
                "Yandex Geocoder returned no objects."
            )

        geo_object = members[0]["GeoObject"]

        try:
            position = (
                geo_object["Point"]["pos"]
            )
        except KeyError as exc:
            raise YandexAPIError(
                "Coordinates are missing "
                "in Yandex response."
            ) from exc

        try:
            lon, lat = map(
                float,
                position.split(),
            )
        except (TypeError, ValueError) as exc:
            raise YandexAPIError(
                "Invalid coordinates "
                "in Yandex response."
            ) from exc

        return lat, lon


class YandexSuggest:
    BASE_URL = (
        "https://suggest-maps.yandex.ru/v1/suggest"
    )

    def __init__(
            self,
            api_key: str | None = YANDEX_API_KEY,
    ) -> None:
        self.api_key = api_key

    async def suggest(
            self,
            *,
            text: str,
            city_lat: float,
            city_lon: float,
            results: int = 7,
    ) -> list[dict[str, Any]]:
        if not self.api_key:
            raise YandexAPIError(
                "YANDEX_SUGGEST_API_KEY is not configured."
            )

        params = {
            "apikey": self.api_key,
            "text": text,
            "lang": "ru_RU",

            # Только географические объекты.
            "types": "geo",

            # Возвращаем uri.
            "attrs": "uri",

            # Возвращаем структурированный адрес.
            "print_address": "1",

            # Не больше 10 по документации.
            "results": min(results, 10),

            # Центр поиска — выбранный город.
            "ll": f"{city_lon},{city_lat}",

            # Окно вокруг города.
            "spn": "0.3,0.2",

            # Не позволяем выдаче уходить за окно.
            "strict_bounds": "1",

            # Только Россия.
            "countries": "ru",

            # Не нужно выделение совпадений.
            "highlight": "0",
        }

        try:
            async with httpx.AsyncClient(
                    timeout=5.0,
            ) as client:
                response = await client.get(
                    self.BASE_URL,
                    params=params,
                )
        except httpx.HTTPError as exc:
            raise YandexAPIError(
                "Failed to connect to Yandex Geosuggest."
            ) from exc

        if response.status_code == 403:
            raise YandexAPIError(
                "Yandex Geosuggest rejected "
                "the API key."
            )

        if response.status_code == 429:
            raise YandexAPIError(
                "Yandex Geosuggest rate limit exceeded."
            )

        if response.is_error:
            raise YandexAPIError(
                f"Yandex Geosuggest returned "
                f"HTTP {response.status_code}."
            )

        try:
            data = response.json()
        except ValueError as exc:
            raise YandexAPIError(
                "Yandex Geosuggest returned invalid JSON."
            ) from exc

        return data.get("results", [])
