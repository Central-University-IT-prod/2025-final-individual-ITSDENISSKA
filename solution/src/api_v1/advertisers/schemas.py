from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, AliasChoices


class AdvertiserBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    advertiser_id: UUID
    name: str = Field(..., min_length=1)


class AdvertiserCreate(AdvertiserBase): ...


class Advertiser(AdvertiserBase): ...
