from pathlib import Path

import numpy as np
from catboost import CatBoostRegressor

from .features import (
    build_apartment_features,
    build_house_features,
    build_land_features,
)

from ..config import MODELS_DIR


class RealEstatePredictor:
    def __init__(
            self,
            models_dir: Path = MODELS_DIR,
    ) -> None:
        self.models_dir = Path(models_dir)

        self.apartment_model = self._load_model(
            "apartment_price.cbm"
        )

        self.house_model = self._load_model(
            "house_price.cbm"
        )

        self.land_model = self._load_model(
            "land_price.cbm"
        )

    def _load_model(
            self,
            filename: str,
    ) -> CatBoostRegressor:
        model_path = self.models_dir / filename

        if not model_path.exists():
            raise FileNotFoundError(
                f"Model file not found: {model_path}"
            )

        model = CatBoostRegressor()
        model.load_model(str(model_path))

        return model

    @staticmethod
    def _predict_price(
            model: CatBoostRegressor,
            features,
    ) -> float:
        predicted_log_price = model.predict(features)

        predicted_price = np.expm1(
            predicted_log_price
        )

        return float(predicted_price[0])

    def predict_apartment(
            self,
            *,
            city_name: str,
            lat: float,
            lon: float,
            distance_to_center_km: float,
            area_m2: float,
            rooms: int | None,
            is_studio: int,
            floor: int,
            floors_total: int,
    ) -> float:
        raw_data = {
            "city_name": city_name,
            "lat": lat,
            "lon": lon,
            "distance_to_center_km": distance_to_center_km,
            "area_m2": area_m2,
            "rooms": rooms,
            "is_studio": is_studio,
            "floor": floor,
            "floors_total": floors_total,
        }

        features = build_apartment_features(raw_data)

        return self._predict_price(
            self.apartment_model,
            features,
        )

    def predict_house(
            self,
            *,
            city_name: str,
            lat: float,
            lon: float,
            distance_to_center_km: float,
            house_area_m2: float,
            land_area_m2: float,
    ) -> float:
        raw_data = {
            "city_name": city_name,
            "lat": lat,
            "lon": lon,
            "distance_to_center_km": distance_to_center_km,
            "house_area_m2": house_area_m2,
            "land_area_m2": land_area_m2,
        }

        features = build_house_features(raw_data)

        return self._predict_price(
            self.house_model,
            features,
        )

    def predict_land(
            self,
            *,
            city_name: str,
            lat: float,
            lon: float,
            distance_to_center_km: float,
            land_area_m2: float,
            land_type: str,
    ) -> float:
        raw_data = {
            "city_name": city_name,
            "lat": lat,
            "lon": lon,
            "distance_to_center_km": distance_to_center_km,
            "land_area_m2": land_area_m2,
            "land_type": land_type,
        }

        features = build_land_features(raw_data)

        return self._predict_price(
            self.land_model,
            features,
        )
