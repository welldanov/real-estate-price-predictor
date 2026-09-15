from ...api.providers.yandex import (
    YandexGeocoder,
)
from ...config import CityConfig
from ...ml.predictor import RealEstatePredictor
from ...utils.geo import calculate_distance_km
from ..schemas.prediction import (
    ApartmentPredictionRequest,
    HousePredictionRequest,
    LandPredictionRequest,
)


class PredictionService:
    def __init__(
            self,
            predictor: RealEstatePredictor,
            geocoder: YandexGeocoder,
    ) -> None:
        self.predictor = predictor
        self.geocoder = geocoder

    async def predict(
            self,
            request,
            city: CityConfig,
    ) -> dict:
        lat, lon = (
            await self.geocoder
            .get_coordinates_by_uri(
                request.address.uri,
            )
        )

        distance_to_center_km = (
            calculate_distance_km(
                lat1=lat,
                lon1=lon,
                lat2=city.lat,
                lon2=city.lon,
            )
        )

        if isinstance(
                request,
                ApartmentPredictionRequest,
        ):
            predicted_price = (
                self.predictor.predict_apartment(
                    city_name=city.name,
                    lat=lat,
                    lon=lon,
                    distance_to_center_km=(
                        distance_to_center_km
                    ),
                    area_m2=request.area_m2,
                    rooms=request.rooms,
                    is_studio=int(
                        request.is_studio
                    ),
                    floor=request.floor,
                    floors_total=(
                        request.floors_total
                    ),
                )
            )

        elif isinstance(
                request,
                HousePredictionRequest,
        ):
            predicted_price = (
                self.predictor.predict_house(
                    city_name=city.name,
                    lat=lat,
                    lon=lon,
                    distance_to_center_km=(
                        distance_to_center_km
                    ),
                    house_area_m2=(
                        request.house_area_m2
                    ),
                    land_area_m2=(
                        request.land_area_m2
                    ),
                )
            )

        elif isinstance(
                request,
                LandPredictionRequest,
        ):
            predicted_price = (
                self.predictor.predict_land(
                    city_name=city.name,
                    lat=lat,
                    lon=lon,
                    distance_to_center_km=(
                        distance_to_center_km
                    ),
                    land_area_m2=(
                        request.land_area_m2
                    ),
                    land_type=request.land_type,
                )
            )

        else:
            raise TypeError(
                "Unsupported prediction request."
            )

        return {
            "property_type":
                request.property_type,

            "predicted_price":
                predicted_price,

            "address": {
                "formatted_address": (
                    request.address
                    .formatted_address
                ),
                "lat": lat,
                "lon": lon,
                "distance_to_center_km": (
                    distance_to_center_km
                ),
            },
        }
