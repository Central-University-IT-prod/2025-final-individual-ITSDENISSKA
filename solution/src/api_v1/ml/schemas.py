from pydantic import BaseModel, ConfigDict, PositiveInt, NonNegativeInt
from uuid import UUID


class MLScoreBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    client_id: UUID
    advertiser_id: UUID
    score: NonNegativeInt


class MLScoreCreate(MLScoreBase): ...


class MLScore(MLScoreBase): ...
