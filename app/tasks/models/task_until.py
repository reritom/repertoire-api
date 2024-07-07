from __future__ import annotations

import enum
from datetime import date as _date
from typing import TYPE_CHECKING

from sqlalchemy import Date, Enum, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from .task import Task


class UntilType(enum.Enum):
    stopped = "stopped"
    date = "date"
    amount = "amount"
    completed = "completed"  # For this "on" frequency type


class TaskUntil(Base):
    __tablename__ = "task_untils"

    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[UntilType] = mapped_column(Enum(UntilType), nullable=False)
    amount: Mapped[int | None] = mapped_column(Integer, nullable=True)
    date: Mapped[_date | None] = mapped_column(Date, nullable=True)

    task: Mapped["Task"] = relationship("Task", back_populates="until", uselist=False)

    @property
    def representation(self) -> str:
        if self.type == UntilType.completed:
            return "Completed or I stop it"

        if self.type == UntilType.stopped:
            return "I stop it"

        if self.type == UntilType.date:
            return self.date.strftime("%Y-%m-%d")

        if self.type == UntilType.amount:
            if self.amount == 1:
                return "Done once"
            if self.amount == 2:
                return "Done twice"
            else:
                return f"Done {self.amount} times"

        # Wont get here
