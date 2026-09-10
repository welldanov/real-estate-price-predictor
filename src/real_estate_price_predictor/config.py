from dataclasses import dataclass


@dataclass(frozen=True)
class CityConfig:
    id: int
    name: str
    lat: float
    lon: float


CITIES: dict[int, CityConfig] = {
    650210: CityConfig(
        id=650210,
        name="Альметьевск",
        lat=54.900000,
        lon=52.300000,
    ),
}

CATEGORY_TYPES: dict[int, str] = {
    24: "apartment",
    25: "house",
    26: "land",
}

BASE_URL = "https://www.avito.ru"
