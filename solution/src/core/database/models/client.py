from uuid import UUID, uuid4

from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database.models.base import Base
from src.core.utils import enums


class Client(Base):
    id = None
    client_id: Mapped[UUID] = mapped_column(
        name="id",
        primary_key=True,
        default=lambda: uuid4(),
    )
    login: Mapped[str]
    age: Mapped[int]
    location: Mapped[str]
    gender: Mapped[enums.GenderEnum] = mapped_column(
        ENUM(enums.GenderEnum, create_type=False)
    )
