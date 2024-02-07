from datetime import date, time

import pytest

from app.tasks.models.task_frequency import FrequencyPeriod, FrequencyType, Weekday
from app.tasks.schemas.task_schema import (
    TaskFrequencyCreationSchema,
)


def test_task_frequency_creation_schema_ok__on__date():
    TaskFrequencyCreationSchema(
        amount=1,
        type=FrequencyType.on,
        once_on_date=date(2023, 12, 25),
    )


def test_task_frequency_creation_schema_ok__on__date_and_time():
    TaskFrequencyCreationSchema(
        amount=1,
        type=FrequencyType.on,
        once_on_date=date(2023, 12, 25),
        once_at_time=time(12, 0, 0),
    )


def test_task_frequency_creation_schema_ok__per__once_per_week_no_specific_day():
    TaskFrequencyCreationSchema(
        amount=1,
        type=FrequencyType.per,
        period=FrequencyPeriod.week,
    )


def test_task_frequency_creation_schema_ok__per__once_per_week_with_specific_day():
    TaskFrequencyCreationSchema(
        amount=1,
        type=FrequencyType.per,
        period=FrequencyPeriod.week,
        once_per_weekday=Weekday.monday,
    )


def test_task_frequency_creation_schema_ok__per__once_per_week_with_specific_day_and_time():
    TaskFrequencyCreationSchema(
        amount=1,
        type=FrequencyType.per,
        period=FrequencyPeriod.week,
        once_per_weekday=Weekday.monday,
        once_at_time=time(12, 0, 0),
    )


def test_task_frequency_creation_schema_ok__this():
    TaskFrequencyCreationSchema(
        amount=1,
        type=FrequencyType.this,
        period=FrequencyPeriod.week,
    )


def test_task_frequency_creation_schema_failure__per__twice_per_week_with_specific_day_and_time():
    with pytest.raises(ValueError) as ctx:
        TaskFrequencyCreationSchema(
            amount=2,
            type=FrequencyType.per,
            period=FrequencyPeriod.week,
            once_per_weekday=Weekday.monday,
            once_at_time=time(12, 0, 0),
        )

    assert ctx.value.error_count() == 1
    assert (
        ctx.value.errors()[0]["msg"]
        == "Specific dates, times, days, are only supported when the frequency is once per period"
    )


def test_task_frequency_creation_schema_failure__on__with_non_one_amount():
    with pytest.raises(ValueError) as ctx:
        TaskFrequencyCreationSchema(
            amount=2,
            type=FrequencyType.on,
            once_on_date=date(2024, 12, 25),
            once_at_time=time(12, 0, 0),
        )

    assert ctx.value.error_count() == 1
    assert (
        ctx.value.errors()[0]["msg"]
        == "Amount must be 1 when task is 'on' a specific date"
    )


def test_task_frequency_creation_schema_failure__on__with_no_date():
    with pytest.raises(ValueError) as ctx:
        TaskFrequencyCreationSchema(
            amount=1,
            type=FrequencyType.on,
            once_at_time=time(12, 0, 0),
        )

    assert ctx.value.error_count() == 1
    assert ctx.value.errors()[0]["msg"] == "Specific date must be set"


def test_task_frequency_creation_schema_failure__on__with_period():
    with pytest.raises(ValueError) as ctx:
        TaskFrequencyCreationSchema(
            amount=1,
            type=FrequencyType.on,
            once_on_date=date(2024, 12, 25),
            period=FrequencyPeriod.week,
        )

    assert ctx.value.error_count() == 1
    assert ctx.value.errors()[0]["msg"] == "Period shouldn't be set for specific events"


def test_task_frequency_creation_schema_failure__on__with_weekday_set():
    with pytest.raises(ValueError) as ctx:
        TaskFrequencyCreationSchema(
            amount=1,
            type=FrequencyType.on,
            once_on_date=date(2024, 12, 25),
            once_per_weekday=Weekday.friday,
        )

    assert ctx.value.error_count() == 1
    assert (
        ctx.value.errors()[0]["msg"]
        == "Unexpected value set: once per weekday should not defined"
    )


def test_task_frequency_creation_schema_failure__per__without_period():
    with pytest.raises(ValueError) as ctx:
        TaskFrequencyCreationSchema(
            amount=1,
            type=FrequencyType.per,
        )

    assert ctx.value.error_count() == 1
    assert ctx.value.errors()[0]["msg"] == "Period must be set"


@pytest.mark.parametrize(
    "field,value",
    [
        ("once_at_time", time(12, 0, 0)),
        ("once_on_date", date(2023, 12, 25)),
        ("once_per_weekday", Weekday.friday),
    ],
)
def test_task_frequency_creation_schema_failure__per__unexpected_field_for_non_one_frequency(
    field, value
):
    with pytest.raises(ValueError) as ctx:
        TaskFrequencyCreationSchema(
            amount=2,
            type=FrequencyType.per,
            period=FrequencyPeriod.week,
            **{field: value},
        )

    assert ctx.value.error_count() == 1
    assert (
        ctx.value.errors()[0]["msg"]
        == "Specific dates, times, days, are only supported when the frequency is once per period"
    )


def test_task_frequency_creation_schema_failure__per__once_per_week_for_non_weekly_period():
    with pytest.raises(ValueError) as ctx:
        TaskFrequencyCreationSchema(
            amount=1,
            type=FrequencyType.per,
            period=FrequencyPeriod.month,
            once_per_weekday=Weekday.friday,
        )

    assert ctx.value.error_count() == 1
    assert (
        ctx.value.errors()[0]["msg"]
        == "Specific weekday requires the period to be weekly"
    )


@pytest.mark.parametrize(
    "field,value",
    [
        ("once_at_time", time(12, 0, 0)),
        ("once_on_date", date(2023, 12, 25)),
        ("once_per_weekday", Weekday.friday),
    ],
)
def test_task_frequency_creation_schema_failure__this__with_unexpected_fields(
    field, value
):
    with pytest.raises(ValueError) as ctx:
        TaskFrequencyCreationSchema(
            amount=1,
            type=FrequencyType.this,
            period=FrequencyPeriod.month,
            **{field: value},
        )

    assert ctx.value.error_count() == 1
    assert (
        ctx.value.errors()[0]["msg"]
        == "Unexpected value set: once at time, once on date, and once per weekday should not be defined"
    )


def test_task_frequency_creation_schema_failure__this__without_period():
    with pytest.raises(ValueError) as ctx:
        TaskFrequencyCreationSchema(
            amount=1,
            type=FrequencyType.this,
        )

    assert ctx.value.error_count() == 1
    assert ctx.value.errors()[0]["msg"] == "Period must be set"
