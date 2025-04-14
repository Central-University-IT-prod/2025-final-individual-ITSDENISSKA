from uuid import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, UniqueConstraint
from src.core.database.models.base import Base


class MLScore(Base):
    client_id: Mapped[UUID] = mapped_column(ForeignKey("clients.id"), nullable=False)
    advertiser_id: Mapped[UUID] = mapped_column(
        ForeignKey("advertisers.id"), nullable=False
    )
    score: Mapped[float] = mapped_column(nullable=False)

    __table_args__ = (
        UniqueConstraint("client_id", "advertiser_id", name="uix_client_advertiser"),
    )
