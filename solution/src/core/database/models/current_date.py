from sqlalchemy.orm import Mapped
from src.core.database.models.base import Base


class CurrentDate(Base):
    __tablename__ = "current_date"

    current_date: Mapped[int]
