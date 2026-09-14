from dataclasses import dataclass


@dataclass(frozen=True)
class TrainingConfig:
    random_seed: int = 42

    test_size: float = 0.20
    cv_folds: int = 5

    iterations: int = 1500
    learning_rate: float = 0.03
    depth: int = 6

    l2_leaf_reg: float = 5.0
    random_strength: float = 1.0

    loss_function: str = "RMSE"
    eval_metric: str = "RMSE"

    early_stopping_rounds: int = 100
