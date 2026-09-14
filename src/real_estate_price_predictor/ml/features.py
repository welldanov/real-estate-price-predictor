import numpy as np
import pandas as pd


def prepare_apartment_features(
        df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.Series]:
    data = df.copy()

    data["floor_ratio"] = (data["floor"] / data["floors_total"])

    data["area_per_room"] = np.where(
        data["rooms"].notna() & (data["rooms"] > 0),
        data["area_m2"] / data["rooms"],
        data["area_m2"],
    )

    data["is_top_floor"] = (data["floor"] == data["floors_total"]).astype(int)

    data["is_first_floor"] = (data["floor"] == 1).astype(int)

    features = [
        "city_name",
        "lat",
        "lon",
        "distance_to_center_km",

        "area_m2",
        "rooms",
        "is_studio",
        "floor",
        "floors_total",

        "floor_ratio",
        "area_per_room",
        "is_top_floor",
        "is_first_floor",
    ]

    x = data[features].copy()
    y = data["price"].copy()

    x["city_name"] = x["city_name"].fillna("unknown")

    return x, y


def prepare_house_features(
        df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.Series]:
    data = df.copy()

    data["land_to_house_ratio"] = (data["land_area_m2"] / data["house_area_m2"])

    data["house_area_share"] = (
            data["house_area_m2"] /
            (
                    data["house_area_m2"] +
                    data["land_area_m2"]
            )
    )

    features = [
        "city_name",
        "lat",
        "lon",
        "distance_to_center_km",

        "house_area_m2",
        "land_area_m2",

        "land_to_house_ratio",
        "house_area_share",
    ]

    x = data[features].copy()
    y = data["price"].copy()

    x["city_name"] = x["city_name"].fillna("unknown")

    return x, y


def prepare_land_features(
        df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.Series]:
    data = df.copy()

    features = [
        "city_name",
        "lat",
        "lon",
        "distance_to_center_km",
        "land_area_m2",
        "land_type",
    ]

    x = data[features].copy()
    y = data["price"].copy()

    x["city_name"] = x["city_name"].fillna("unknown")
    x["land_type"] = x["land_type"].fillna("unknown")

    return x, y
