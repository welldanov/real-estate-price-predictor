from pathlib import Path

from dataclasses import dataclass

ROOT_DIR = Path(__file__).resolve().parents[1]

DB_PATH = ROOT_DIR / "data" / "real_estate.db"
SCHEMA_PATH = ROOT_DIR / "sql" / "schema.sql"
MODELS_DIR = ROOT_DIR / "models"
ANALYSIS_DIR = ROOT_DIR / "analysis"


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
