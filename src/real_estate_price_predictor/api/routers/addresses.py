from fastapi import (
    APIRouter,
    HTTPException,
    Query,
    Request,
)

from ...config import CITIES
from ..schemas.address import (
    AddressSearchResponse,
)
from ..services.address_service import (
    AddressService,
)
from ..providers.yandex import (
    YandexAPIError,
)

router = APIRouter(
    prefix="/addresses",
    tags=["addresses"],
)


@router.get(
    "/search",
    response_model=AddressSearchResponse,
)
async def search_addresses(
        request: Request,
        city_id: int = Query(gt=0),
        query: str = Query(
            min_length=2,
            max_length=200,
        ),
) -> AddressSearchResponse:
    city = CITIES.get(city_id)

    if city is None:
        raise HTTPException(
            status_code=404,
            detail="City not found.",
        )

    service: AddressService = (
        request.app.state.address_service
    )

    try:
        items = await service.search(
            city=city,
            query=query.strip(),
        )

    except YandexAPIError as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        ) from exc

    return AddressSearchResponse(
        items=items,
    )
