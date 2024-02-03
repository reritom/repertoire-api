from __future__ import annotations

import enum
from datetime import date as _date
from typing import TYPE_CHECKING

from sqlalchemy import Date, Enum, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base

if TYPE_CHECKING:
    pass


class UntilType(enum.Enum):
    stopped = "stopped"
    date = "date"
    amount = "amount"
    completed = "completed"


class TaskUntil(Base):
    __tablename__ = "task_untils"

    id: Mapped[int] = mapped_column(primary_key=True)
    # task: Mapped[Task] = relationship(back_populates="until", uselist=False)
    type: Mapped[UntilType | None] = mapped_column(Enum(UntilType), nullable=False)
    amount: Mapped[int | None] = mapped_column(Integer, nullable=True)
    date: Mapped[_date | None] = mapped_column(Date, nullable=True)
