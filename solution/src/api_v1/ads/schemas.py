from uuid import UUID

from pydantic import BaseModel, ConfigDict, HttpUrl


class AdBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ad_id: UUID
    ad_title: str
    ad_text: str
    advertiser_id: UUID
    files: list[HttpUrl] | None = None


class Ad(AdBase): ...
