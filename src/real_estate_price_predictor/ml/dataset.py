import pandas as pd

def load_apartments(conn) -> pd.DataFrame:
    query = """
        SELECT
            l.id AS listing_id,
            l.price,
            l.url,
            l.formatted_address,
            l.city_id,
            c.name AS city_name,
            l.lat,
            l.lon,
            l.distance_to_center_km,
            l.parsed_at,

            a.area_m2,
            a.rooms,
            a.is_studio,
            a.floor,
            a.floors_total

        FROM listings l
        JOIN cities c
            ON c.id = l.city_id
        JOIN apartments a
            ON a.listing_id = l.id

        WHERE l.price > 0
    """

    return pd.read_sql_query(query, conn)


def load_houses(conn) -> pd.DataFrame:
    query = """
        SELECT
            l.id AS listing_id,
            l.price,
            l.url,
            l.formatted_address,
            l.city_id,
            c.name AS city_name,
            l.lat,
            l.lon,
            l.distance_to_center_km,
            l.parsed_at,

            h.house_area_m2,
            h.land_area_m2

        FROM listings l
        JOIN cities c
            ON c.id = l.city_id
        JOIN houses h
            ON h.listing_id = l.id

        WHERE l.price > 0
    """

    return pd.read_sql_query(query, conn)


def load_lands(conn) -> pd.DataFrame:
    query = """
        SELECT
            l.id AS listing_id,
            l.price,
            l.url,
            l.formatted_address,
            l.city_id,
            c.name AS city_name,
            l.lat,
            l.lon,
            l.distance_to_center_km,
            l.parsed_at,

            ld.land_area_m2,
            ld.land_type

        FROM listings l
        JOIN cities c
            ON c.id = l.city_id
        JOIN lands ld
            ON ld.listing_id = l.id

        WHERE l.price > 0
    """

    return pd.read_sql_query(query, conn)