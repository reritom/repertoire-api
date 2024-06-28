from datetime import date, time

from app.tasks.daos.task_frequency_dao import TaskFrequencyDao
from app.tasks.models.task_frequency import FrequencyPeriod, FrequencyType, Weekday


def test_create_task_frequency_ok(session):
    frequency = TaskFrequencyDao(session=session).create(
        type=FrequencyType.on,
        amount=10,
        period=FrequencyPeriod.month,
        once_on_date=date(2020, 12, 25),
        once_per_weekday=Weekday.monday,
        once_at_time=time(12, 0, 0),
    )

    assert frequency.type == FrequencyType.on
    assert frequency.amount == 10
    assert frequency.period == FrequencyPeriod.month
    assert frequency.once_on_date == date(2020, 12, 25)
    assert frequency.once_per_weekday == Weekday.monday
    assert frequency.once_at_time == time(12, 0, 0)
