from dataclasses import dataclass

import numpy as np
import pandas as pd

from catboost import CatBoostRegressor


@dataclass
class TrainingResult:
    model: CatBoostRegressor
    best_iteration: int


def train_model(
        x_train: pd.DataFrame,
        y_train: pd.Series,
        x_valid: pd.DataFrame,
        y_valid: pd.Series,
        cat_features: list[str],
        config,
) -> TrainingResult:
    model = CatBoostRegressor(
        iterations=config.iterations,
        learning_rate=config.learning_rate,
        depth=config.depth,

        loss_function=config.loss_function,
        eval_metric=config.eval_metric,

        l2_leaf_reg=config.l2_leaf_reg,
        random_strength=config.random_strength,

        random_seed=config.random_seed,

        verbose=False,

        od_type="Iter",
        od_wait=config.early_stopping_rounds,

        allow_writing_files=False
    )

    y_train_log = np.log1p(y_train)
    y_valid_log = np.log1p(y_valid)

    model.fit(
        x_train,
        y_train_log,

        cat_features=cat_features,

        eval_set=(x_valid, y_valid_log),

        use_best_model=True,
    )

    return TrainingResult(
        model=model,
        best_iteration=model.get_best_iteration(),
    )
