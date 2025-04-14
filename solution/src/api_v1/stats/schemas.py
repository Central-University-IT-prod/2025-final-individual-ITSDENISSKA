from pydantic import BaseModel, NonNegativeInt, NonNegativeFloat


class StatBase(BaseModel):
    impressions_count: NonNegativeInt
    clicks_count: NonNegativeInt
    conversion: NonNegativeFloat
    spent_impressions: NonNegativeFloat
    spent_clicks: NonNegativeFloat
    spent_total: NonNegativeFloat


class Stat(StatBase): ...


class DailyStat(StatBase):
    date: NonNegativeInt
