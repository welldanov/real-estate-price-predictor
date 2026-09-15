from pydantic import BaseModel, Field


class AddressSuggestion(BaseModel):
    title: str
    subtitle: str | None = None

    formatted_address: str | None = None

    uri: str = Field(
        min_length=1,
    )


class AddressSearchResponse(BaseModel):
    items: list[AddressSuggestion]