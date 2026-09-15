from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv
import os

ROOT_DIR = Path(__file__).resolve().parents[2]

DB_PATH = ROOT_DIR / "data" / "real_estate.db"
SCHEMA_PATH = ROOT_DIR / "sql" / "schema.sql"
MODELS_DIR = ROOT_DIR / "models"
ANALYSIS_DIR = ROOT_DIR / "analysis"

BASE_URL = "https://www.avito.ru"

load_dotenv(ROOT_DIR / ".env")

YANDEX_API_KEY = os.getenv(
    "YANDEX_API_KEY"
)


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
