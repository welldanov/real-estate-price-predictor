import re
import math

from ..config import CityConfig, CITIES, CATEGORY_TYPES, BASE_URL
from ..utils.geo import calculate_distance_km

from ..ingestion.models import (
    ApartmentData,
    CityData,
    CategoryData,
    HouseData,
    LandData,
    ListingData,
    ListingType,
    NormalizedListing,
)
from ..ingestion.validator import (
    AvitoListingSchema,
)


def classify_listing(
        category_id: int,
) -> ListingType:
    try:
        return ListingType(CATEGORY_TYPES[category_id])

    except KeyError as exc:
        raise ValueError(
            f"Unsupported Avito category id: {category_id}"
        ) from exc


def get_city_config(
        city_id: int,
) -> CityConfig:
    try:
        return CITIES[city_id]

    except KeyError as exc:
        raise ValueError(
            f"Unknown city id: {city_id}"
        ) from exc


def build_url(url_path: str) -> str:
    if url_path.startswith("http://"):
        return url_path

    if url_path.startswith("https://"):
        return url_path

    return f"{BASE_URL}{url_path}"


def parse_apartment_title(
        title: str,
) -> tuple[
    float | None,
    int | None,
    bool | None,
    int | None,
    int | None,
]:
    area_m2 = None
    rooms = None
    is_studio = None
    floor = None
    floors_total = None

    area_match = re.search(
        r"([\d\s]+(?:[.,]\d+)?)\s*м²",
        title,
        flags=re.IGNORECASE,
    )

    if area_match:
        area_m2 = float(
            area_match.group(1)
            .replace(" ", "")
            .replace(",", ".")
        )

    rooms_match = re.search(
        r"(\d+)\s*[--–]?\s*к\.",
        title,
        flags=re.IGNORECASE,
    )

    if rooms_match:
        rooms = int(rooms_match.group(1))
        is_studio = False

    elif "студия" in title.lower():
        is_studio = True
        rooms = None

    floor_match = re.search(
        r"(\d+)\s*/\s*(\d+)\s*эт",
        title,
        flags=re.IGNORECASE,
    )

    if floor_match:
        floor = int(floor_match.group(1))
        floors_total = int(floor_match.group(2))

    return (
        area_m2,
        rooms,
        is_studio,
        floor,
        floors_total,
    )


def parse_house_title(
        title: str,
) -> tuple[float | None, float | None]:
    house_area_m2 = None
    land_area_m2 = None

    house_match = re.search(
        r"Дом\s+([\d\s]+(?:[.,]\d+)?)\s*м²",
        title,
        flags=re.IGNORECASE,
    )

    if house_match:
        house_area_m2 = float(
            house_match.group(1)
            .replace(" ", "")
            .replace(",", ".")
        )

    land_match = re.search(
        r"на\s+участке\s+([\d\s]+(?:[.,]\d+)?)\s*сот",
        title,
        flags=re.IGNORECASE,
    )

    if land_match:
        hundreds = float(
            land_match.group(1)
            .replace(" ", "")
            .replace(",", ".")
        )

        land_area_m2 = hundreds * 100

    return house_area_m2, land_area_m2


def parse_land_title(
        title: str,
) -> tuple[float | None, str | None]:
    land_area_m2 = None
    land_type = None

    area_match = re.search(
        r"Участок\s+([\d\s]+(?:[.,]\d+)?)\s*сот",
        title,
        flags=re.IGNORECASE,
    )

    if area_match:
        hundreds = float(
            area_match.group(1)
            .replace(" ", "")
            .replace(",", ".")
        )

        land_area_m2 = hundreds * 100

    type_match = re.search(
        r"\(([^)]+)\)",
        title,
    )

    if type_match:
        land_type = type_match.group(1).strip()

    return land_area_m2, land_type


def parse_coordinates(
        item: AvitoListingSchema,
) -> tuple[float, float]:
    if item.coords is None:
        raise ValueError(
            "Listing coordinates are missing"
        )

    try:
        lat = float(item.coords.lat)
        lon = float(item.coords.lng)

    except (TypeError, ValueError) as exc:
        raise ValueError(
            "Listing coordinates are invalid"
        ) from exc

    if not -90 <= lat <= 90:
        raise ValueError(
            f"Invalid latitude: {lat}"
        )

    if not -180 <= lon <= 180:
        raise ValueError(
            f"Invalid longitude: {lon}"
        )

    return lat, lon


def parse_formatted_address(
        item: AvitoListingSchema,
) -> str:
    if item.geo is None:
        raise ValueError(
            "Geo information is missing"
        )

    address = item.geo.formattedAddress

    if not address:
        raise ValueError(
            "Formatted address is missing"
        )

    return address


def normalize(item: AvitoListingSchema) -> NormalizedListing:
    listing_type = classify_listing(item.category.id)
    city_config = get_city_config(item.location.id)
    lat, lon = parse_coordinates(item)
    formatted_address = parse_formatted_address(item)
    distance_to_center_km = calculate_distance_km(lat1=city_config.lat, lon1=city_config.lon, lat2=lat, lon2=lon)

    if not math.isfinite(distance_to_center_km):
        raise ValueError("Calculated distance is not finite")

    city = CityData(
        id=city_config.id,
        name=city_config.name,
        lat=city_config.lat,
        lon=city_config.lon,
    )
    category = CategoryData(
        id=item.category.id,
        name=item.category.name,
    )
    listing = ListingData(
        id=item.id,
        city_id=item.location.id,
        category_id=item.category.id,
        price=item.priceDetailed.value,
        formatted_address=formatted_address,
        district=None,
        lat=lat,
        lon=lon,
        distance_to_center_km=distance_to_center_km,
        description=item.description,
        url=build_url(item.urlPath),
        parsed_at=item.parsed_at,
    )

    match listing_type:
        case ListingType.APARTMENT:
            area_m2, rooms, is_studio, floor, floors_total = parse_apartment_title(item.title)

            if area_m2 is None:
                raise ValueError("Apartment area is missing")
            if is_studio is None:
                raise ValueError("Apartment type cannot be determined")
            if floor is None or floors_total is None:
                raise ValueError("Apartment floor information is missing")

            specific_data = ApartmentData(
                listing_id=item.id,
                area_m2=area_m2,
                rooms=rooms,
                is_studio=is_studio,
                floor=floor,
                floors_total=floors_total,
            )

        case ListingType.HOUSE:
            house_area_m2, land_area_m2 = parse_house_title(item.title)

            if house_area_m2 is None:
                raise ValueError("House area is missing")
            if land_area_m2 is None:
                raise ValueError("Land area for house is missing")

            specific_data = HouseData(
                listing_id=item.id,
                house_area_m2=house_area_m2,
                land_area_m2=land_area_m2,
            )

        case ListingType.LAND:
            land_area_m2, land_type = parse_land_title(item.title)

            if land_area_m2 is None:
                raise ValueError("Land area is missing")
            if land_type is None:
                raise ValueError("Land type is missing")

            specific_data = LandData(
                listing_id=item.id,
                land_area_m2=land_area_m2,
                land_type=land_type,
            )

        case _:
            raise ValueError(f"Unsupported listing type: {listing_type}")

    type_field_map = {
        ListingType.APARTMENT: "apartment",
        ListingType.HOUSE: "house",
        ListingType.LAND: "land",
    }

    return NormalizedListing(
        listing_type=listing_type,
        city=city,
        category=category,
        listing=listing,
        **{type_field_map[listing_type]: specific_data}
    )
