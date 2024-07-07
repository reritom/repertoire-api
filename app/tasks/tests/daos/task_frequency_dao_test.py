from datetime import date, time

import pytest
from sqlalchemy.exc import NoResultFound

from app.accounts.tests.factories import UserFactory
from app.tasks.daos.task_frequency_dao import TaskFrequencyDao
from app.tasks.models.task_frequency import (
    FrequencyPeriod,
    FrequencyType,
    TaskFrequency,
    Weekday,
)
from app.tasks.tests.factories import TaskFactory, TaskFrequencyFactory


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


def test_delete_task_frequency_ok(session):
    # Noise
    UserFactory.create_batch(3)
    TaskFrequencyFactory.create_batch(4)

    frequency = TaskFrequencyFactory()

    TaskFrequencyDao(session=session).delete(id=frequency.id)

    assert session.get(TaskFrequency, frequency.id) is None


def test_delete_task_frequency_failure_used_by_task(session):
    task = TaskFactory()
    frequency = task.frequency

    with pytest.raises(NoResultFound):
        # TODO maybe raise an integrity error
        TaskFrequencyDao(session=session).delete(
            id=frequency.id,
        )
