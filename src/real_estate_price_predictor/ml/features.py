import numpy as np
import pandas as pd

APARTMENT_FEATURES = [
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

APARTMENT_CATEGORICAL_FEATURES = [
    "city_name",
]


def _build_apartment_features(df: pd.DataFrame) -> pd.DataFrame:
    data = df.copy()

    data["floor_ratio"] = np.where(
        data["floors_total"] > 0,
        data["floor"] / data["floors_total"],
        np.nan,
    )

    data["area_per_room"] = np.where(
        data["rooms"].notna() & (data["rooms"] > 0),
        data["area_m2"] / data["rooms"],
        data["area_m2"],
    )

    data["is_top_floor"] = (
            data["floor"] == data["floors_total"]
    ).astype(int)

    data["is_first_floor"] = (
            data["floor"] == 1
    ).astype(int)

    features = data[APARTMENT_FEATURES].copy()

    features["city_name"] = (
        features["city_name"]
        .fillna("unknown")
        .astype(str)
    )

    return features


def prepare_apartment_features(
        df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.Series]:
    if "price" not in df.columns:
        raise ValueError(
            "Apartment training dataset must contain 'price' column."
        )

    x = _build_apartment_features(df)
    y = df["price"].copy()

    return x, y


def build_apartment_features(
        data: dict | pd.DataFrame,
) -> pd.DataFrame:
    if isinstance(data, dict):
        df = pd.DataFrame([data])
    elif isinstance(data, pd.DataFrame):
        df = data.copy()
    else:
        raise TypeError(
            "data must be a dict or pandas DataFrame."
        )

    return _build_apartment_features(df)


HOUSE_FEATURES = [
    "city_name",
    "lat",
    "lon",
    "distance_to_center_km",
    "house_area_m2",
    "land_area_m2",
    "land_to_house_ratio",
    "house_area_share",
]

HOUSE_CATEGORICAL_FEATURES = [
    "city_name",
]


def _build_house_features(df: pd.DataFrame) -> pd.DataFrame:
    data = df.copy()

    data["land_to_house_ratio"] = np.where(
        data["house_area_m2"] > 0,
        data["land_area_m2"] / data["house_area_m2"],
        np.nan,
    )

    data["house_area_share"] = np.where(
        data["land_area_m2"] > 0,
        data["house_area_m2"] / data["land_area_m2"],
        np.nan,
    )

    features = data[HOUSE_FEATURES].copy()

    features["city_name"] = (
        features["city_name"]
        .fillna("unknown")
        .astype(str)
    )

    return features


def prepare_house_features(
        df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.Series]:
    if "price" not in df.columns:
        raise ValueError(
            "House training dataset must contain 'price' column."
        )

    x = _build_house_features(df)
    y = df["price"].copy()

    return x, y


def build_house_features(
        data: dict | pd.DataFrame,
) -> pd.DataFrame:
    if isinstance(data, dict):
        df = pd.DataFrame([data])
    elif isinstance(data, pd.DataFrame):
        df = data.copy()
    else:
        raise TypeError(
            "data must be a dict or pandas DataFrame."
        )

    return _build_house_features(df)


LAND_FEATURES = [
    "city_name",
    "lat",
    "lon",
    "distance_to_center_km",
    "land_area_m2",
    "land_type",
]

LAND_CATEGORICAL_FEATURES = [
    "city_name",
    "land_type",
]


def _build_land_features(df: pd.DataFrame) -> pd.DataFrame:
    data = df.copy()

    features = data[LAND_FEATURES].copy()

    features["city_name"] = (
        features["city_name"]
        .fillna("unknown")
        .astype(str)
    )

    features["land_type"] = (
        features["land_type"]
        .fillna("unknown")
        .astype(str)
    )

    return features


def prepare_land_features(
        df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.Series]:
    if "price" not in df.columns:
        raise ValueError(
            "Land training dataset must contain 'price' column."
        )

    x = _build_land_features(df)
    y = df["price"].copy()

    return x, y


def build_land_features(
        data: dict | pd.DataFrame,
) -> pd.DataFrame:
    if isinstance(data, dict):
        df = pd.DataFrame([data])
    elif isinstance(data, pd.DataFrame):
        df = data.copy()
    else:
        raise TypeError(
            "data must be a dict or pandas DataFrame."
        )

    return _build_land_features(df)
