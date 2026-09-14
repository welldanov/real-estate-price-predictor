# from pathlib import Path
#
# import numpy as np
# from catboost import CatBoostRegressor
#
# from real_estate_price_predictor.ml.config import TrainingConfig
# from real_estate_price_predictor.ml.dataset import (
#     load_apartments,
#     load_houses,
#     load_lands,
# )
# from real_estate_price_predictor.ml.features import (
#     prepare_apartment_features,
#     prepare_house_features,
#     prepare_land_features,
# )
# from real_estate_price_predictor.ml.split import split_dataset
# from real_estate_price_predictor.ml.evaluator import (
#     calculate_metrics,
#     print_metrics,
# )
# from real_estate_price_predictor.ml.artifacts import (
#     save_model,
#     save_metadata,
# )
#
# ROOT_DIR = Path(__file__).resolve().parents[1]
#
# DB_PATH = ROOT_DIR / "data" / "real_estate.db"
# MODELS_DIR = ROOT_DIR / "models"
#
#
# def train_one_model(
#         model_name: str,
#         data,
#         prepare_features,
#         categorical_features: list[str],
#         config: TrainingConfig,
# ) -> None:
#     print()
#     print("=" * 70)
#     print(f"Training model: {model_name}")
#     print("=" * 70)
#
#     x, y = prepare_features(data)
#
#     print(f"Dataset size: {len(x)}")
#     print(f"Features: {list(x.columns)}")
#     print(f"Categorical features: {categorical_features}")
#
#     (
#         x_train,
#         x_test,
#         y_train,
#         y_test,
#     ) = split_dataset(
#         x,
#         y,
#         test_size=config.test_size,
#         random_state=config.random_seed,
#     )
#
#     print()
#     print(f"Train size: {len(x_train)}")
#     print(f"Test size:  {len(x_test)}")
#
#     y_train_log = np.log1p(y_train)
#
#     model = CatBoostRegressor(
#         iterations=config.iterations,
#         learning_rate=config.learning_rate,
#         depth=config.depth,
#
#         loss_function=config.loss_function,
#         eval_metric=config.eval_metric,
#
#         l2_leaf_reg=config.l2_leaf_reg,
#         random_strength=config.random_strength,
#
#         random_seed=config.random_seed,
#
#         verbose=100,
#     )
#
#     print()
#     print("Starting training...")
#
#     model.fit(
#         x_train,
#         y_train_log,
#         cat_features=categorical_features,
#     )
#
#     predictions_log = model.predict(x_test)
#
#     predictions = np.expm1(predictions_log)
#
#     metrics = calculate_metrics(
#         y_test,
#         predictions,
#     )
#
#     print()
#     print("TEST RESULTS")
#     print("-" * 70)
#
#     print_metrics(metrics)
#
#     model_path = (
#             MODELS_DIR /
#             f"{model_name}_price.cbm"
#     )
#
#     metadata_path = (
#             MODELS_DIR /
#             f"{model_name}_metadata.json"
#     )
#
#     save_model(
#         model,
#         model_path,
#     )
#
#     save_metadata(
#         {
#             "model_type": model_name,
#
#             "target": "price",
#             "target_transform": "log1p",
#
#             "features": list(x.columns),
#
#             "categorical_features": categorical_features,
#
#             "training_samples": len(x_train),
#             "test_samples": len(x_test),
#
#             "iterations": config.iterations,
#             "learning_rate": config.learning_rate,
#             "depth": config.depth,
#
#             "l2_leaf_reg": config.l2_leaf_reg,
#             "random_strength": config.random_strength,
#
#             "random_seed": config.random_seed,
#
#             "metrics": metrics,
#         },
#         metadata_path,
#     )
#
#     print()
#     print(f"Model saved:    {model_path}")
#     print(f"Metadata saved: {metadata_path}")
#
#
# def main() -> None:
#     config = TrainingConfig()
#
#     if not DB_PATH.exists():
#         raise FileNotFoundError(
#             f"Database not found: {DB_PATH}"
#         )
#
#     MODELS_DIR.mkdir(
#         parents=True,
#         exist_ok=True,
#     )
#
#     print("Loading data from database...")
#
#     apartments = load_apartments(DB_PATH)
#     houses = load_houses(DB_PATH)
#     lands = load_lands(DB_PATH)
#
#     print()
#     print("Loaded datasets:")
#     print(f"  Apartments: {len(apartments)}")
#     print(f"  Houses:     {len(houses)}")
#     print(f"  Lands:      {len(lands)}")
#
#     train_one_model(
#         model_name="apartment",
#         data=apartments,
#         prepare_features=prepare_apartment_features,
#         categorical_features=[
#             "city_name",
#         ],
#         config=config,
#     )
#
#     train_one_model(
#         model_name="house",
#         data=houses,
#         prepare_features=prepare_house_features,
#         categorical_features=[
#             "city_name",
#         ],
#         config=config,
#     )
#
#     train_one_model(
#         model_name="land",
#         data=lands,
#         prepare_features=prepare_land_features,
#         categorical_features=[
#             "city_name",
#             "land_type",
#         ],
#         config=config,
#     )
#
#
# if __name__ == "__main__":
#     main()


from pathlib import Path

import numpy as np
import pandas as pd
from catboost import CatBoostRegressor

from real_estate_price_predictor.config import ANALYSIS_DIR, DB_PATH, MODELS_DIR

from real_estate_price_predictor.database.connection import create_connection

from real_estate_price_predictor.ml.config import TrainingConfig

from real_estate_price_predictor.ml.dataset import (
    load_apartments,
    load_houses,
    load_lands,
)
from real_estate_price_predictor.ml.features import (
    prepare_apartment_features,
    prepare_house_features,
    prepare_land_features,
)
from real_estate_price_predictor.ml.split import split_dataset
from real_estate_price_predictor.ml.evaluator import (
    calculate_metrics,
    print_metrics,
)


# ============================================================
# BASELINES
# ============================================================

def calculate_median_baseline(
        y_train: pd.Series,
        y_test: pd.Series,
) -> dict[str, float]:
    median_price = y_train.median()

    predictions = np.full(
        shape=len(y_test),
        fill_value=median_price,
        dtype=float,
    )

    return calculate_metrics(y_test, predictions)


def calculate_price_per_m2_baseline(
        x_train: pd.DataFrame,
        x_test: pd.DataFrame,
        y_train: pd.Series,
        y_test: pd.Series,
) -> dict[str, float]:
    train_price_per_m2 = y_train / x_train["area_m2"]

    median_price_per_m2 = train_price_per_m2.median()

    predictions = (
            median_price_per_m2 * x_test["area_m2"].to_numpy()
    )

    return calculate_metrics(y_test, predictions)


# ============================================================
# STATISTICS
# ============================================================

def print_price_statistics(
        y: pd.Series,
        model_name: str,
) -> None:
    print("\n" + "=" * 70)
    print(f"PRICE STATISTICS: {model_name}")
    print("=" * 70)

    percentiles = y.quantile(
        [
            0.01,
            0.05,
            0.25,
            0.50,
            0.75,
            0.95,
            0.99,
        ]
    )

    print(f"Count:       {len(y)}")
    print(f"Mean:        {y.mean():,.0f}")
    print(f"Std:         {y.std():,.0f}")
    print(f"Min:         {y.min():,.0f}")

    for percentile, value in percentiles.items():
        print(
            f"{percentile * 100:>5.0f}%:        "
            f"{value:,.0f}"
        )

    print(f"Max:         {y.max():,.0f}")

    if y.median() != 0:
        print(
            f"Mean/Median: "
            f"{y.mean() / y.median():.2f}"
        )


# ============================================================
# ERROR ANALYSIS
# ============================================================

def build_error_analysis(
        metadata: pd.DataFrame,
        y_true: pd.Series,
        y_pred: np.ndarray,
) -> pd.DataFrame:
    result = metadata.copy()

    result["actual_price"] = np.asarray(y_true)
    result["predicted_price"] = np.asarray(y_pred)

    result["error"] = (
            result["predicted_price"]
            - result["actual_price"]
    )

    result["absolute_error"] = (
        result["error"].abs()
    )

    result["percentage_error"] = (
            result["absolute_error"]
            / result["actual_price"]
            * 100
    )

    result["signed_percentage_error"] = (
            result["error"]
            / result["actual_price"]
            * 100
    )

    return result.sort_values(
        "absolute_error",
        ascending=False,
    )


def print_worst_predictions(
        errors: pd.DataFrame,
        n: int = 10,
) -> None:
    print("\n" + "=" * 70)
    print(f"WORST PREDICTIONS BY ABSOLUTE ERROR — TOP {n}")
    print("=" * 70)

    columns = [
        "listing_id",
        "actual_price",
        "predicted_price",
        "error",
        "percentage_error",
    ]

    available_columns = [
        column
        for column in columns
        if column in errors.columns
    ]

    print(
        errors[available_columns]
        .head(n)
        .to_string(index=False)
    )


def print_worst_percentage_predictions(
        errors: pd.DataFrame,
        n: int = 10,
) -> None:
    print("\n" + "=" * 70)
    print(f"WORST PREDICTIONS BY PERCENTAGE ERROR — TOP {n}")
    print("=" * 70)

    columns = [
        "listing_id",
        "actual_price",
        "predicted_price",
        "percentage_error",
        "error",
    ]

    available_columns = [
        column
        for column in columns
        if column in errors.columns
    ]

    result = (
        errors
        .sort_values(
            "percentage_error",
            ascending=False,
        )
        .head(n)
    )

    print(
        result[available_columns]
        .to_string(index=False)
    )


# ============================================================
# FEATURE IMPORTANCE
# ============================================================

def save_feature_importance(
        model: CatBoostRegressor,
        model_name: str,
) -> Path:
    importance = model.get_feature_importance()

    result = pd.DataFrame({
        "feature": model.feature_names_,
        "importance": importance,
    }).sort_values(
        "importance",
        ascending=False,
    )

    path = (
            ANALYSIS_DIR
            / f"{model_name}_feature_importance.csv"
    )

    result.to_csv(
        path,
        index=False,
    )

    return path


# ============================================================
# TRAIN ONE MODEL
# ============================================================

def train_one_model(
        model_name: str,
        data: pd.DataFrame,
        prepare_features,
        categorical_features: list[str],
        config: TrainingConfig,
) -> None:
    print("\n")
    print("#" * 80)
    print(f"# TRAINING: {model_name}")
    print("#" * 80)

    # --------------------------------------------------------
    # Statistics
    # --------------------------------------------------------

    print_price_statistics(
        data["price"],
        model_name,
    )

    # --------------------------------------------------------
    # Prepare features
    # --------------------------------------------------------

    X, y = prepare_features(data)

    # --------------------------------------------------------
    # IMPORTANT:
    # metadata сохраняем отдельно.
    #
    # X сохраняет исходный index data.
    # Поэтому после train_test_split индексы
    # x_train/x_test будут соответствовать data.
    # --------------------------------------------------------

    metadata = data[
        [
            "listing_id",
            "url",
            "formatted_address",
            "city_name",
            "lat",
            "lon",
            "distance_to_center_km",
        ]
    ].copy()

    # --------------------------------------------------------
    # Split
    # --------------------------------------------------------

    X_train, X_test, y_train, y_test = split_dataset(
        X,
        y,
        test_size=config.test_size,
        random_state=config.random_seed,
    )

    print("\nDataset split:")
    print(f"Train: {len(X_train)}")
    print(f"Test:  {len(X_test)}")

    # --------------------------------------------------------
    # Metadata для test.
    #
    # ВАЖНО:
    # берем metadata именно по индексам X_test,
    # поэтому ID никогда не потеряется.
    # --------------------------------------------------------

    test_metadata = metadata.loc[
        X_test.index
    ].copy()

    # --------------------------------------------------------
    # Baseline: median
    # --------------------------------------------------------

    print("\n" + "-" * 70)
    print("BASELINE: MEDIAN PRICE")
    print("-" * 70)

    baseline_metrics = calculate_median_baseline(
        y_train,
        y_test,
    )

    print_metrics(baseline_metrics)

    # --------------------------------------------------------
    # Baseline: price per m2
    # только для квартир
    # --------------------------------------------------------

    price_per_m2_metrics = None

    if "area_m2" in X_train.columns:
        print("\n" + "-" * 70)
        print("BASELINE: MEDIAN PRICE PER M2")
        print("-" * 70)

        price_per_m2_metrics = (
            calculate_price_per_m2_baseline(
                X_train,
                X_test,
                y_train,
                y_test,
            )
        )

        print_metrics(price_per_m2_metrics)

    # --------------------------------------------------------
    # Target = log1p(price)
    # --------------------------------------------------------

    y_train_log = np.log1p(y_train)

    # --------------------------------------------------------
    # CatBoost
    # --------------------------------------------------------

    model = CatBoostRegressor(
        iterations=config.iterations,
        learning_rate=config.learning_rate,
        depth=config.depth,
        loss_function=config.loss_function,
        eval_metric=config.eval_metric,
        l2_leaf_reg=config.l2_leaf_reg,
        random_strength=config.random_strength,
        random_seed=config.random_seed,
        verbose=100,
    )

    print("\nTraining CatBoost...")

    model.fit(
        X_train,
        y_train_log,
        cat_features=categorical_features,
    )

    # --------------------------------------------------------
    # Prediction
    # --------------------------------------------------------

    y_pred_log = model.predict(X_test)

    y_pred = np.expm1(y_pred_log)

    # защита от отрицательных предсказаний
    y_pred = np.maximum(y_pred, 0)

    # --------------------------------------------------------
    # Metrics
    # --------------------------------------------------------

    metrics = calculate_metrics(
        y_test,
        y_pred,
    )

    print("\n" + "=" * 70)
    print("MODEL METRICS")
    print("=" * 70)

    print_metrics(metrics)

    # --------------------------------------------------------
    # Improvement
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("IMPROVEMENT VS BASELINES")
    print("=" * 70)

    baseline_mae = baseline_metrics["mae"]

    mae_improvement = (
                              1 - metrics["mae"] / baseline_mae
                      ) * 100

    mdape_improvement = (
                                1
                                - metrics["median_absolute_percentage_error"]
                                / baseline_metrics[
                                    "median_absolute_percentage_error"
                                ]
                        ) * 100

    print(
        f"MAE improvement vs median: "
        f"{mae_improvement:.2f}%"
    )

    print(
        f"MdAPE improvement vs median: "
        f"{mdape_improvement:.2f}%"
    )

    if price_per_m2_metrics is not None:
        p2m_mae_improvement = (
                                      1
                                      - metrics["mae"]
                                      / price_per_m2_metrics["mae"]
                              ) * 100

        print(
            f"MAE improvement vs price/m²: "
            f"{p2m_mae_improvement:.2f}%"
        )

    # --------------------------------------------------------
    # Error analysis
    # --------------------------------------------------------

    errors = build_error_analysis(
        metadata=test_metadata,
        y_true=y_test,
        y_pred=y_pred,
    )

    print_worst_predictions(
        errors,
        n=10,
    )

    print_worst_percentage_predictions(
        errors,
        n=10,
    )

    # --------------------------------------------------------
    # Save errors
    # --------------------------------------------------------

    errors_path = (
            ANALYSIS_DIR
            / f"{model_name}_errors.csv"
    )

    errors.to_csv(
        errors_path,
        index=False,
    )

    print("\nError analysis saved to:")
    print(errors_path)

    # --------------------------------------------------------
    # Feature importance
    # --------------------------------------------------------

    feature_importance_path = (
        save_feature_importance(
            model,
            model_name,
        )
    )

    print("\nFeature importance saved to:")
    print(feature_importance_path)

    # --------------------------------------------------------
    # Save model
    # --------------------------------------------------------

    model_path = (
            MODELS_DIR
            / f"{model_name}.cbm"
    )

    model.save_model(model_path)

    print("\nModel saved to:")
    print(model_path)


# ============================================================
# MAIN
# ============================================================

def main() -> None:
    config = TrainingConfig()

    with create_connection(DB_PATH) as conn:
        apartments = load_apartments(conn)
        houses = load_houses(conn)
        lands = load_lands(conn)

    print("\nLoaded datasets:")
    print(f"Apartments: {len(apartments)}")
    print(f"Houses:     {len(houses)}")
    print(f"Lands:      {len(lands)}")

    # --------------------------------------------------------
    # Apartments
    # --------------------------------------------------------

    train_one_model(
        model_name="apartment_price",
        data=apartments,
        prepare_features=prepare_apartment_features,
        categorical_features=[
            "city_name",
        ],
        config=config,
    )

    # --------------------------------------------------------
    # Houses
    # --------------------------------------------------------

    train_one_model(
        model_name="house_price",
        data=houses,
        prepare_features=prepare_house_features,
        categorical_features=[
            "city_name",
        ],
        config=config,
    )

    # --------------------------------------------------------
    # Lands
    # --------------------------------------------------------

    train_one_model(
        model_name="land_price",
        data=lands,
        prepare_features=prepare_land_features,
        categorical_features=[
            "city_name",
            "land_type",
        ],
        config=config,
    )


if __name__ == "__main__":
    main()
