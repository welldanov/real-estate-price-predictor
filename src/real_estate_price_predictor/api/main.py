from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ..ml.predictor import RealEstatePredictor

from .providers.yandex import (
    YandexGeocoder,
    YandexSuggest,
)
from .routers import (
    addresses,
    cities,
    health,
    predictions,
)
from .services.address_service import (
    AddressService,
)
from .services.prediction_service import (
    PredictionService,
)


@asynccontextmanager
async def lifespan(
        app: FastAPI,
):
    # ML models.
    predictor = RealEstatePredictor()

    # Yandex clients.
    geocoder = YandexGeocoder()
    suggest = YandexSuggest()

    # Services.
    app.state.address_service = (
        AddressService(
            suggest=suggest,
        )
    )

    app.state.prediction_service = (
        PredictionService(
            predictor=predictor,
            geocoder=geocoder,
        )
    )

    yield


app = FastAPI(
    title="Real Estate Price Predictor API",
    description="API для прогнозирования стоимости объектов недвижимости.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    health.router,
)

app.include_router(
    cities.router,
)

app.include_router(
    addresses.router,
)

app.include_router(
    predictions.router,
)
