from typing import Annotated, Literal

from pydantic import BaseModel, Field


class AddressSelection(BaseModel):
    uri: str = Field(
        min_length=1,
        max_length=2000,
    )

    formatted_address: str = Field(
        min_length=1,
        max_length=500,
    )


class BasePredictionRequest(BaseModel):
    city_id: int = Field(
        gt=0,
    )

    address: AddressSelection


class ApartmentPredictionRequest(
    BasePredictionRequest
):
    property_type: Literal["apartment"]

    area_m2: float = Field(
        gt=0,
        le=1000,
    )

    rooms: int | None = Field(
        default=None,
        ge=0,
        le=20,
    )

    is_studio: bool = False

    floor: int = Field(
        ge=1,
        le=200,
    )

    floors_total: int = Field(
        ge=1,
        le=200,
    )


class HousePredictionRequest(
    BasePredictionRequest
):
    property_type: Literal["house"]

    house_area_m2: float = Field(
        gt=0,
        le=5000,
    )

    land_area_m2: float = Field(
        gt=0,
        le=100000,
    )


class LandPredictionRequest(
    BasePredictionRequest
):
    property_type: Literal["land"]

    land_area_m2: float = Field(
        gt=0,
        le=100000,
    )

    land_type: str = Field(
        min_length=1,
        max_length=100,
    )


PredictionRequest = Annotated[
    (
            ApartmentPredictionRequest
            | HousePredictionRequest
            | LandPredictionRequest
    ),
    Field(
        discriminator="property_type",
    ),
]


class PredictionAddress(BaseModel):
    formatted_address: str

    lat: float
    lon: float

    distance_to_center_km: float


class PredictionResponse(BaseModel):
    property_type: Literal[
        "apartment",
        "house",
        "land",
    ]

    predicted_price: float

    address: PredictionAddress
