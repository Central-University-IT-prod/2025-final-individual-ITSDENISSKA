from uuid import UUID
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    AliasChoices,
    NonNegativeInt,
)
import re

from src.core.utils import enums


class ClientBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    client_id: UUID
    login: str = Field(..., min_length=1)
    age: NonNegativeInt
    location: str = Field(..., min_length=1)
    gender: enums.GenderEnum


class Client(ClientBase): ...


class ClientCreate(ClientBase): ...
