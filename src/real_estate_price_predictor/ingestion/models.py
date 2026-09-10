from dataclasses import dataclass
from enum import StrEnum
from datetime import datetime


class ListingType(StrEnum):
    APARTMENT = "apartment"
    HOUSE = "house"
    LAND = "land"


@dataclass(frozen=True)
class CityData:
    id: int
    name: str
    lat: float
    lon: float


@dataclass(frozen=True)
class CategoryData:
    id: int
    name: str


@dataclass(frozen=True)
class ListingData:
    id: int
    city_id: int
    category_id: int

    price: int

    formatted_address: str
    district: str | None

    lat: float
    lon: float

    distance_to_center_km: float

    description: str

    url: str
    parsed_at: datetime


@dataclass(frozen=True)
class ApartmentData:
    listing_id: int

    area_m2: float
    rooms: int | None
    is_studio: bool
    floor: int
    floors_total: int


@dataclass(frozen=True)
class HouseData:
    listing_id: int

    house_area_m2: float
    land_area_m2: float


@dataclass(frozen=True)
class LandData:
    listing_id: int

    land_area_m2: float
    land_type: str


@dataclass(frozen=True)
class NormalizedListing:
    listing_type: ListingType

    city: CityData
    category: CategoryData
    listing: ListingData

    apartment: ApartmentData | None = None
    house: HouseData | None = None
    land: LandData | None = None