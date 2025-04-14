from pydantic import BaseModel


class LLMModerateResponse(BaseModel):
    status: bool
    reason: str | None


class LLMGeneratedAd(BaseModel):
    ad_text: str
    ad_title: str
