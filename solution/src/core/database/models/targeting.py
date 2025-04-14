from sqlalchemy import Enum, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column

from src.core.database.models import Base
from src.core.utils import enums


class Targeting(Base):
    gender: Mapped[enums.ExtendedGenderEnum] = mapped_column(
        Enum(enums.ExtendedGenderEnum),
        nullable=True,
    )
    age_from: Mapped[int] = mapped_column(nullable=True)
    age_to: Mapped[int] = mapped_column(nullable=True)
    location: Mapped[str] = mapped_column(nullable=True)

    campaign_id: Mapped[str] = mapped_column(
        ForeignKey("campaigns.id"),
        unique=True,
    )
    campaign: Mapped["Campaign"] = relationship(
        "Campaign",
        lazy="subquery",
        back_populates="targeting",
    )
