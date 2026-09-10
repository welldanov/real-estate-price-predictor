import sqlite3

from real_estate_price_predictor.ingestion.models import (
    ApartmentData,
    CategoryData,
    CityData,
    HouseData,
    LandData,
    ListingData,
)


def upsert_city(
    conn: sqlite3.Connection,
    city: CityData,
) -> None:
    conn.execute(
        """
        INSERT INTO cities (id,
                            name,
                            lat,
                            lon)
        VALUES (?, ?, ?, ?) ON CONFLICT(id) DO
        UPDATE SET
            name = excluded.name,
            lat = excluded.lat,
            lon = excluded.lon
        """,
        (
            city.id,
            city.name,
            city.lat,
            city.lon,
        ),
    )


def upsert_category(
    conn: sqlite3.Connection,
    category: CategoryData,
) -> None:
    conn.execute(
        """
        INSERT INTO categories (
            id,
            name
        )
        VALUES (?, ?)
        ON CONFLICT(id) DO UPDATE SET
            name = excluded.name
        """,
        (
            category.id,
            category.name,
        ),
    )


def upsert_listing(
    conn: sqlite3.Connection,
    listing: ListingData,
) -> None:
    conn.execute(
        """
        INSERT INTO listings (
            id,
            city_id,
            category_id,
            price,
            formatted_address,
            district,
            lat,
            lon,
            distance_to_center_km,
            description,
            url,
            parsed_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            city_id = excluded.city_id,
            category_id = excluded.category_id,
            price = excluded.price,
            formatted_address = excluded.formatted_address,
            district = excluded.district,
            lat = excluded.lat,
            lon = excluded.lon,
            distance_to_center_km = excluded.distance_to_center_km,
            description = excluded.description,
            url = excluded.url,
            parsed_at = excluded.parsed_at
        """,
        (
            listing.id,
            listing.city_id,
            listing.category_id,
            listing.price,
            listing.formatted_address,
            listing.district,
            listing.lat,
            listing.lon,
            listing.distance_to_center_km,
            listing.description,
            listing.url,
            listing.parsed_at.isoformat(),
        ),
    )


def upsert_apartment(
    conn: sqlite3.Connection,
    apartment: ApartmentData,
) -> None:
    conn.execute(
        """
        INSERT INTO apartments (
            listing_id,
            area_m2,
            rooms,
            is_studio,
            floor,
            floors_total
        )
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(listing_id) DO UPDATE SET
            area_m2 = excluded.area_m2,
            rooms = excluded.rooms,
            is_studio = excluded.is_studio,
            floor = excluded.floor,
            floors_total = excluded.floors_total
        """,
        (
            apartment.listing_id,
            apartment.area_m2,
            apartment.rooms,
            int(apartment.is_studio),
            apartment.floor,
            apartment.floors_total,
        ),
    )


def upsert_house(
    conn: sqlite3.Connection,
    house: HouseData,
) -> None:
    conn.execute(
        """
        INSERT INTO houses (
            listing_id,
            house_area_m2,
            land_area_m2
        )
        VALUES (?, ?, ?)
        ON CONFLICT(listing_id) DO UPDATE SET
            house_area_m2 = excluded.house_area_m2,
            land_area_m2 = excluded.land_area_m2
        """,
        (
            house.listing_id,
            house.house_area_m2,
            house.land_area_m2,
        ),
    )


def upsert_land(
    conn: sqlite3.Connection,
    land: LandData,
) -> None:
    conn.execute(
        """
        INSERT INTO lands (
            listing_id,
            land_area_m2,
            land_type
        )
        VALUES (?, ?, ?)
        ON CONFLICT(listing_id) DO UPDATE SET
            land_area_m2 = excluded.land_area_m2,
            land_type = excluded.land_type
        """,
        (
            land.listing_id,
            land.land_area_m2,
            land.land_type,
        ),
    )