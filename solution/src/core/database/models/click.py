from uuid import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey
from src.core.database.models.base import Base


class UniqueClick(Base):
    __tablename__ = "unique_clicks"

    client_id: Mapped[UUID] = mapped_column(ForeignKey("clients.id"), primary_key=True)
    campaign_id: Mapped[str] = mapped_column(
        ForeignKey("campaigns.id"), primary_key=True
    )
    cost: Mapped[float]
    date: Mapped[int] = mapped_column(primary_key=True)
