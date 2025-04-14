from uuid import uuid4, UUID

from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database.models.base import Base
from src.core.utils import enums


class Advertiser(Base):
    id = None
    advertiser_id: Mapped[UUID] = mapped_column(
        name="id",
        primary_key=True,
        default=lambda: uuid4(),
    )
    name: Mapped[str]

    campaigns: Mapped[list["Campaign"]] = relationship(
        "Campaign",
        back_populates="advertiser",
        cascade="all, delete-orphan",
        lazy="subquery",
    )
