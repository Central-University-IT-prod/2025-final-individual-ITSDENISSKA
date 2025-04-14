from uuid import UUID, uuid4
from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship, Mapped, mapped_column

from src.core.database.models import Base


class Campaign(Base):
    id = None
    campaign_id: Mapped[UUID] = mapped_column(
        name="id",
        primary_key=True,
        default=lambda: uuid4(),
    )
    advertiser_id: Mapped[UUID] = mapped_column(ForeignKey("advertisers.id"))
    impressions_limit: Mapped[int]
    clicks_limit: Mapped[int]
    cost_per_impression: Mapped[float]
    cost_per_click: Mapped[float]
    ad_title: Mapped[str]
    ad_text: Mapped[str]
    start_date: Mapped[int]
    end_date: Mapped[int]
    is_deleted: Mapped[bool] = mapped_column(default=False, nullable=True)
    files: Mapped[list[str]] = mapped_column(JSON, nullable=True)

    advertiser: Mapped["Advertiser"] = relationship(
        "Advertiser",
        back_populates="campaigns",
        lazy="subquery",
    )

    targeting: Mapped["Targeting"] = relationship(
        "Targeting",
        back_populates="campaign",
        lazy="subquery",
        uselist=False,
        cascade="all, delete-orphan",
    )
