from __future__ import annotations

import enum
from datetime import date as _date
from typing import TYPE_CHECKING

from sqlalchemy import Date, Enum, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from .task import Task


class UntilType(enum.Enum):
    stopped = "stopped"
    date = "date"
    amount = "amount"
    completed = "completed"


class TaskUntil(Base):
    __tablename__ = "task_untils"

    id: Mapped[int] = mapped_column(primary_key=True)

    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"), nullable=False)
    task: Mapped[Task] = relationship(back_populates="until", uselist=False)

    type: Mapped[UntilType | None] = mapped_column(Enum(UntilType), nullable=False)
    amount: Mapped[int | None] = mapped_column(Integer, nullable=True)
    date: Mapped[_date | None] = mapped_column(Date, nullable=True)
