from typing import Self
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    HttpUrl,
    model_validator,
    Field,
    NonNegativeInt,
    NonNegativeFloat,
)

from src.core.utils import enums


class TargetingBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    gender: enums.ExtendedGenderEnum | None = None
    age_from: NonNegativeInt | None = None
    age_to: NonNegativeInt | None = None
    location: str | None = Field(None, min_length=1)

    @model_validator(mode="after")
    def validate_dates(self) -> Self:
        if self.age_from and self.age_to and self.age_from > self.age_to:
            raise ValueError("age_from должно быть меньше или равно age_to")
        return self


class TargetingCreate(TargetingBase): ...


class TargetingUpdate(TargetingBase): ...


class CampaignBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    impressions_limit: NonNegativeInt
    clicks_limit: NonNegativeInt
    cost_per_impression: NonNegativeFloat
    cost_per_click: NonNegativeFloat
    ad_title: str = Field(..., min_length=1)
    ad_text: str = Field(..., min_length=1)
    start_date: NonNegativeInt
    end_date: NonNegativeInt
    targeting: TargetingBase | None = None
    files: list[HttpUrl] | None = None

    @model_validator(mode="after")
    def validate_dates(self) -> Self:
        if self.start_date > self.end_date:
            raise ValueError("start_date должно быть меньше или равно end_date")
        if self.clicks_limit > self.impressions_limit:
            raise ValueError("clicks_limit не может быть больше impressions_limit")

        return self


class CampaignCreate(CampaignBase): ...


class Campaign(CampaignBase):
    campaign_id: UUID
    advertiser_id: UUID
    files: list[HttpUrl] | None | list[str] = None


class CampaignUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    cost_per_impression: NonNegativeFloat | None = None
    cost_per_click: NonNegativeFloat | None = None
    ad_title: str | None = None
    ad_text: str | None = None
    targeting: TargetingBase | None = None
    files: list[HttpUrl] | None = None
