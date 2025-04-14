from pydantic import BaseModel, NonNegativeInt


class DateBase(BaseModel):
    current_date: NonNegativeInt


class Date(DateBase): ...
