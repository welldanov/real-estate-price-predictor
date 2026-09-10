import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd
from catboost import CatBoostRegressor
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)
from sklearn.model_selection import train_test_split


# ============================================================
# CONFIG
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DB_PATH = PROJECT_ROOT / "data" / "real_estate.db"
MODEL_PATH = PROJECT_ROOT / "models" / "catboost_price.cbm"

TEST_SIZE = 0.2
RANDOM_STATE = 42


# ============================================================
# SQL
# ============================================================

QUERY = """
    SELECT
        listings.id AS listing_id,
        listings.price,
    
        listings.lat,
        listings.lon,
    
        categories.name AS category,
    
        apartments.area_m2,
        apartments.rooms,
        apartments.is_studio,
        apartments.floor,
        apartments.floors_total,
    
        houses.house_area_m2,
        houses.land_area_m2 AS house_land_area_m2,
    
        lands.land_area_m2,
        lands.land_type
    
    FROM listings
    
    LEFT JOIN categories
        ON categories.id = listings.category_id
    
    LEFT JOIN apartments
        ON apartments.listing_id = listings.id
    
    LEFT JOIN houses
        ON houses.listing_id = listings.id
    
    LEFT JOIN lands
        ON lands.listing_id = listings.id
    
    ORDER BY listings.id
"""


# ============================================================
# LOAD DATA
# ============================================================

def load_data(db_path: Path) -> pd.DataFrame:
    if not db_path.exists():
        raise FileNotFoundError(
            f"Database not found: {db_path}"
        )

    with sqlite3.connect(db_path) as connection:
        dataframe = pd.read_sql_query(
            QUERY,
            connection,
        )

    if dataframe.empty:
        raise ValueError(
            "Database contains no listings"
        )

    return dataframe


# ============================================================
# PREPARE FEATURES
# ============================================================

def prepare_data(
    dataframe: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.Series]:

    dataframe = dataframe.copy()

    # Target
    dataframe["price"] = pd.to_numeric(
        dataframe["price"],
        errors="coerce",
    )

    dataframe = dataframe[
        dataframe["price"].notna()
        & (dataframe["price"] > 0)
    ].copy()

    # Только нужные признаки.
    feature_columns = [
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

    features = dataframe[feature_columns].copy()
    target = dataframe["price"].copy()

    # Categorical features.
    categorical_columns = [
        "category",
        "land_type",
    ]

    for column in categorical_columns:
        features[column] = (
            features[column]
            .fillna("unknown")
            .astype(str)
        )

    # Boolean.
    features["is_studio"] = (
        features["is_studio"]
        .fillna(0)
        .astype(int)
    )

    # Numeric features.
    numeric_columns = [
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
    ]

    for column in numeric_columns:
        features[column] = pd.to_numeric(
            features[column],
            errors="coerce",
        )

    # Удаляем признаки, которые полностью NULL.
    empty_columns = [
        column
        for column in features.columns
        if features[column].isna().all()
    ]

    if empty_columns:
        features = features.drop(
            columns=empty_columns,
        )

    print()
    print("Features:")

    for column in features.columns:
        if column in categorical_columns:
            feature_type = "categorical"
        else:
            feature_type = "numeric"

        print(
            f"  {column:<25} {feature_type}"
        )

    print()
    print(f"Objects: {len(features)}")
    print(f"Features: {len(features.columns)}")

    return features, target


# ============================================================
# TRAIN
# ============================================================

def train_model(
    x_train: pd.DataFrame,
    y_train: pd.Series,
    x_test: pd.DataFrame,
    y_test: pd.Series,
) -> CatBoostRegressor:

    categorical_features = [
        column
        for column in [
            "category",
            "land_type",
        ]
        if column in x_train.columns
    ]

    model = CatBoostRegressor(
        iterations=1500,
        learning_rate=0.05,
        depth=8,
        loss_function="RMSE",
        eval_metric="MAE",
        random_seed=RANDOM_STATE,
        early_stopping_rounds=100,
        verbose=100,
    )

    model.fit(
        x_train,
        y_train,
        cat_features=categorical_features,
        eval_set=(x_test, y_test),
        use_best_model=True,
    )

    return model


# ============================================================
# EVALUATION
# ============================================================

def evaluate_model(
    model: CatBoostRegressor,
    x_test: pd.DataFrame,
    y_test: pd.Series,
) -> pd.DataFrame:

    predictions = model.predict(x_test)

    predictions = np.maximum(
        predictions,
        0,
    )

    mae = mean_absolute_error(
        y_test,
        predictions,
    )

    rmse = np.sqrt(
        mean_squared_error(
            y_test,
            predictions,
        )
    )

    r2 = r2_score(
        y_test,
        predictions,
    )

    print()
    print("=" * 60)
    print("MODEL QUALITY")
    print("=" * 60)

    print(f"MAE:  {mae:,.0f} ₽")
    print(f"RMSE: {rmse:,.0f} ₽")
    print(f"R²:   {r2:.4f}")

    result = x_test.copy()

    result["actual_price"] = y_test
    result["predicted_price"] = predictions

    result["absolute_error"] = (
        result["predicted_price"]
        - result["actual_price"]
    ).abs()

    result["error_percent"] = (
        result["absolute_error"]
        / result["actual_price"]
        * 100
    )

    return result


# ============================================================
# SHOW REAL OBJECTS
# ============================================================

def show_predictions(
    predictions: pd.DataFrame,
) -> None:

    print()
    print("=" * 60)
    print("REAL TEST OBJECTS")
    print("=" * 60)

    result = predictions.sample(
        n=min(20, len(predictions)),
        random_state=RANDOM_STATE,
    )

    for _, row in result.head(20).iterrows():

        print(
            f"{row['category']:<12} | "
            f"actual={row['actual_price']:>10,.0f} ₽ | "
            f"predicted={row['predicted_price']:>10,.0f} ₽ | "
            f"error={row['absolute_error']:>9,.0f} ₽ "
            f"({row['error_percent']:.1f}%)"
        )


# ============================================================
# FEATURE IMPORTANCE
# ============================================================

def show_feature_importance(
    model: CatBoostRegressor,
    features: pd.DataFrame,
) -> None:

    importance = model.get_feature_importance()

    result = pd.DataFrame(
        {
            "feature": features.columns,
            "importance": importance,
        }
    )

    result = result.sort_values(
        "importance",
        ascending=False,
    )

    print()
    print("=" * 60)
    print("FEATURE IMPORTANCE")
    print("=" * 60)

    for _, row in result.iterrows():
        print(
            f"{row['feature']:<25} "
            f"{row['importance']:>8.2f}"
        )


# ============================================================
# SAVE MODEL
# ============================================================

def save_model(
    model: CatBoostRegressor,
    model_path: Path,
) -> None:

    model_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    model.save_model(
        model_path,
    )

    print()
    print(f"Model saved: {model_path}")


# ============================================================
# MAIN
# ============================================================

def main() -> None:

    print("=" * 60)
    print("REAL ESTATE PRICE PREDICTOR")
    print("=" * 60)

    # Load data.
    print()
    print("Loading data...")

    dataframe = load_data(
        DB_PATH,
    )

    print(
        f"Loaded: {len(dataframe)} objects"
    )

    # Prepare features.
    features, target = prepare_data(
        dataframe,
    )

    # Train / test split.
    x_train, x_test, y_train, y_test = train_test_split(
        features,
        target,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
    )

    print()
    print(f"Train: {len(x_train)}")
    print(f"Test:  {len(x_test)}")

    # Train.
    print()
    print("=" * 60)
    print("TRAINING CATBOOST")
    print("=" * 60)

    model = train_model(
        x_train=x_train,
        y_train=y_train,
        x_test=x_test,
        y_test=y_test,
    )

    # Evaluate.
    predictions = evaluate_model(
        model=model,
        x_test=x_test,
        y_test=y_test,
    )

    # Real objects.
    show_predictions(
        predictions,
    )

    # Feature importance.
    show_feature_importance(
        model=model,
        features=features,
    )

    # Save.
    save_model(
        model=model,
        model_path=MODEL_PATH,
    )

    print()
    print("Done.")


if __name__ == "__main__":
    main()