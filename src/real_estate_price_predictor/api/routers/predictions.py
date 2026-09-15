from fastapi import (
    APIRouter,
    HTTPException,
    Request,
)

from ...config import CITIES
from ..providers.yandex import (
    YandexAPIError,
)
from ..schemas.prediction import (
    PredictionRequest,
    PredictionResponse,
)
from ..services.prediction_service import (
    PredictionService,
)

router = APIRouter(
    prefix="/predict",
    tags=["prediction"],
)


@router.post(
    "",
    response_model=PredictionResponse,
)
async def predict(
        request: Request,
        prediction_request: PredictionRequest,
) -> PredictionResponse:
    city = CITIES.get(
        prediction_request.city_id
    )

    if city is None:
        raise HTTPException(
            status_code=404,
            detail="City not found.",
        )

    service: PredictionService = (
        request.app.state.prediction_service
    )

    try:
        result = await service.predict(
            request=prediction_request,
            city=city,
        )

    except YandexAPIError as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        ) from exc

    return PredictionResponse(
        **result,
    )
