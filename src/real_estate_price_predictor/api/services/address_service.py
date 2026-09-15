from ...api.providers.yandex import (
    YandexSuggest,
)
from ...config import CityConfig


class AddressService:
    def __init__(
            self,
            suggest: YandexSuggest,
    ) -> None:
        self.suggest = suggest

    async def search(
            self,
            *,
            city: CityConfig,
            query: str,
    ) -> list[dict]:
        results = await self.suggest.suggest(
            text=query,
            city_lat=city.lat,
            city_lon=city.lon,
        )

        suggestions = []

        for result in results:
            title = (
                result.get("title", {})
                .get("text", "")
                .strip()
            )

            subtitle = (
                result.get("subtitle", {})
                .get("text")
            )

            address = result.get(
                "address",
                {},
            )

            formatted_address = (
                address.get(
                    "formatted_address"
                )
            )

            uri = result.get("uri")

            if not title or not uri:
                continue

            suggestions.append(
                {
                    "title": title,
                    "subtitle": subtitle,
                    "formatted_address":
                        formatted_address,
                    "uri": uri,
                }
            )

        return suggestions
