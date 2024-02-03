from __future__ import annotations

import enum
from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, Enum, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base

if TYPE_CHECKING:
    pass


class Weekday(enum.Enum):
    monday = "monday"
    tuesday = "tuesday"
    wednesday = "wednesday"
    thursday = "thursday"
    friday = "friday"
    saturday = "saturday"
    sunday = "sunday"


class FrequencyType(enum.Enum):
    per = "per"
    this = "this"
    on = "on"


class FrequencyPeriod(enum.Enum):
    day = "day"
    week = "week"
    month = "month"
    quarter = "quarter"
    year = "year"


class TaskFrequency(Base):
    __tablename__ = "task_frequencies"

    id: Mapped[int] = mapped_column(primary_key=True)
    # task: Mapped[Task] = relationship(back_populates="frequency", uselist=False)
    type: Mapped[FrequencyType] = mapped_column(Enum(FrequencyType), nullable=False)
    period: Mapped[FrequencyPeriod] = mapped_column(
        Enum(FrequencyPeriod), nullable=False
    )
    amount: Mapped[int | None] = mapped_column(Integer, nullable=True)
    once_on_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    once_per_weekday: Mapped[Weekday | None] = mapped_column(
        Enum(Weekday), nullable=True
    )
    once_at_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
