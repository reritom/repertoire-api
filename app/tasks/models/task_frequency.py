from __future__ import annotations

import enum
from datetime import date, time

from sqlalchemy import Boolean, Date, Enum, Integer, Time
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


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


def _format_time(_time: time) -> str:
    return _time.strftime("%I:%M").lstrip("0") + _time.strftime("%p").lower()


def _format_date(_date: date) -> str:
    return _date.strftime("%Y-%m-%d")


class TaskFrequency(Base):
    __tablename__ = "task_frequencies"

    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[FrequencyType] = mapped_column(Enum(FrequencyType), nullable=False)
    period: Mapped[FrequencyPeriod] = mapped_column(
        Enum(FrequencyPeriod), nullable=True
    )
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    use_calendar_period: Mapped[bool] = mapped_column(Boolean, default=True)
    once_on_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    once_per_weekday: Mapped[Weekday | None] = mapped_column(
        Enum(Weekday), nullable=True
    )
    once_at_time: Mapped[time | None] = mapped_column(Time, nullable=True)

    @property
    def representation(self) -> str:
        if self.amount == 1:
            amount_representation = "Once"
        elif self.amount == 2:
            amount_representation = "Twice"
        else:
            amount_representation = f"{self.amount} times"

        if self.type == FrequencyType.this:
            return f"{amount_representation} this{' calendar' if self.use_calendar_period else ''} {self.period.value}"

        if self.type == FrequencyType.on:
            representation = f"Once on {_format_date(self.once_on_date)}"
            if self.once_at_time:
                representation = (
                    f"{representation} at {_format_time(self.once_at_time)}"
                )
            return representation

        if self.type == FrequencyType.per:
            representation = f"{amount_representation} per {self.period.value}"

            if self.amount != 1:
                return representation

            if self.period == FrequencyPeriod.day and self.once_at_time:
                representation = (
                    f"{representation} at {_format_time(self.once_at_time)}"
                )

            elif self.period == FrequencyPeriod.week:
                if self.once_per_weekday:
                    representation = (
                        f"{representation} on {self.once_per_weekday.value}"
                    )
                else:
                    representation = f"{representation} on any day"

                if self.once_at_time:
                    representation = (
                        f"{representation} at {_format_time(self.once_at_time)}"
                    )
                else:
                    representation = f"{representation} at any time"

            return representation

        # We won't reach here
