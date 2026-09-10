from __future__ import annotations

from pathlib import Path

import pandas as pd
from catboost import CatBoostRegressor


# ============================================================
# CONFIG
# ============================================================

MODEL_PATH = (
    Path(__file__).resolve().parents[2]
    / "models"
    / "catboost_price.cbm"
)


FEATURES = [
    "category",
    "lat",
    "lon",
    "area_m2",
    "rooms",
    "is_studio",
    "floor",
    "floors_total",
    "house_area_m2",
    "house_land_area_m2",
    "land_area_m2",
    "land_type",
]

CATEGORICAL_FEATURES = [
    "category",
    "land_type",
]


# ============================================================
# MODEL
# ============================================================

def load_model(model_path: Path) -> CatBoostRegressor:
    if not model_path.exists():
        raise FileNotFoundError(
            f"Model not found: {model_path}"
        )

    model = CatBoostRegressor()
    model.load_model(model_path)

    return model


# ============================================================
# DATA PREPARATION
# ============================================================

def prepare_object(
    object_data: dict,
) -> pd.DataFrame:

    dataframe = pd.DataFrame(
        [object_data],
        columns=FEATURES,
    )

    # Categorical features
    for column in CATEGORICAL_FEATURES:
        dataframe[column] = (
            dataframe[column]
            .fillna("unknown")
            .astype(str)
        )

    # Boolean
    dataframe["is_studio"] = (
        dataframe["is_studio"]
        .fillna(0)
        .astype(int)
    )

    # Numeric features
    numeric_features = [
        column
        for column in FEATURES
        if column not in CATEGORICAL_FEATURES
    ]

    for column in numeric_features:
        dataframe[column] = pd.to_numeric(
            dataframe[column],
            errors="coerce",
        )

    return dataframe


# ============================================================
# PREDICTION
# ============================================================

def predict_price(
    model: CatBoostRegressor,
    object_data: dict,
) -> float:

    features = prepare_object(
        object_data,
    )

    prediction = model.predict(
        features,
    )[0]

    return max(float(prediction), 0.0)


# ============================================================
# EXAMPLE
# ============================================================

def main() -> None:

    print("=" * 60)
    print("REAL ESTATE PRICE PREDICTOR")
    print("=" * 60)

    model = load_model(
        MODEL_PATH,
    )

    # --------------------------------------------------------
    # OBJECT TO PREDICT
    # --------------------------------------------------------

    object_data = {
        "category": "Квартиры",

        # "lat": 54.901222,
        # "lon": 52.251901,

        "lat": 54.890438,
        "lon": 52.268565,

        "area_m2": 42.5,
        "rooms": 1,
        "is_studio": 0,

        "floor": 8,
        "floors_total": 18,

        "house_area_m2": None,
        "house_land_area_m2": None,

        "land_area_m2": None,
        "land_type": None,
    }

    # --------------------------------------------------------
    # PREDICT
    # --------------------------------------------------------

    predicted_price = predict_price(
        model=model,
        object_data=object_data,
    )

    print()
    print("OBJECT")
    print("-" * 60)

    for key, value in object_data.items():
        print(f"{key:<25} {value}")

    print()
    print("=" * 60)
    print(
        f"PREDICTED PRICE: {predicted_price:,.0f} ₽"
    )
    print("=" * 60)


if __name__ == "__main__":
    main()