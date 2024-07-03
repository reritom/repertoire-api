from datetime import date, time
from typing import Optional

from app.shared.dao import BaseDao
from app.tasks.models.task_frequency import (
    FrequencyPeriod,
    FrequencyType,
    TaskFrequency,
    Weekday,
)


class TaskFrequencyDao(BaseDao[TaskFrequency]):
    class Meta:
        model = TaskFrequency

    def create(
        self,
        type: FrequencyType,
        amount: int,
        period: Optional[FrequencyPeriod] = None,
        once_on_date: Optional[date] = None,
        once_per_weekday: Optional[Weekday] = None,
        once_at_time: Optional[time] = None,
        use_calendar_period: bool = True,
    ) -> TaskFrequency:
        frequency = TaskFrequency(
            type=type,
            amount=amount,
            period=period,
            once_on_date=once_on_date,
            once_per_weekday=once_per_weekday,
            once_at_time=once_at_time,
            use_calendar_period=use_calendar_period,
        )

        with self.session.begin_nested():
            self.session.add(frequency)

        self.session.flush()
        return frequency
