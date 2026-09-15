from fastapi import APIRouter

from ...config import CITIES
from ..schemas.city import CityResponse

router = APIRouter(
    prefix="/cities",
    tags=["cities"],
)


@router.get(
    "",
    response_model=list[CityResponse],
)
async def get_cities() -> list[CityResponse]:
    return [
        CityResponse(
            id=city.id,
            name=city.name,
        )
        for city in CITIES.values()
    ]
