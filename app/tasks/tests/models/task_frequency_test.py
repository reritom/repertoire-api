from datetime import date, time

import pytest

from app.tasks.models.task_frequency import (
    FrequencyPeriod,
    FrequencyType,
    TaskFrequency,
    Weekday,
)


@pytest.mark.parametrize(
    "frequency,expected_representation",
    [
        # This - not calendar
        (
            TaskFrequency(
                amount=1,
                type=FrequencyType.this,
                period=FrequencyPeriod.week,
                use_calendar_period=False,
            ),
            "Once this week",
        ),
        (
            TaskFrequency(
                amount=2,
                type=FrequencyType.this,
                period=FrequencyPeriod.month,
                use_calendar_period=False,
            ),
            "Twice this month",
        ),
        (
            TaskFrequency(
                amount=3,
                type=FrequencyType.this,
                use_calendar_period=False,
                period=FrequencyPeriod.year,
            ),
            "3 times this year",
        ),
        # This - calendar
        (
            TaskFrequency(
                amount=1,
                type=FrequencyType.this,
                period=FrequencyPeriod.week,
                use_calendar_period=True,
            ),
            "Once this calendar week",
        ),
        (
            TaskFrequency(
                amount=2,
                type=FrequencyType.this,
                period=FrequencyPeriod.month,
                use_calendar_period=True,
            ),
            "Twice this calendar month",
        ),
        (
            TaskFrequency(
                amount=3,
                type=FrequencyType.this,
                period=FrequencyPeriod.year,
                use_calendar_period=True,
            ),
            "3 times this calendar year",
        ),
        # On
        (
            TaskFrequency(
                amount=1,
                type=FrequencyType.on,
                once_on_date=date(2020, 12, 25),
            ),
            "Once on 2020-12-25",
        ),
        (
            TaskFrequency(
                amount=1,
                type=FrequencyType.on,
                once_on_date=date(2020, 12, 25),
                once_at_time=time(13, 25),
            ),
            "Once on 2020-12-25 at 1:25pm",
        ),
        # Per
        (
            TaskFrequency(
                amount=1,
                type=FrequencyType.per,
                period=FrequencyPeriod.day,
            ),
            "Once per day",
        ),
        (
            TaskFrequency(
                amount=1,
                type=FrequencyType.per,
                period=FrequencyPeriod.day,
                once_at_time=time(12, 20),
            ),
            "Once per day at 12:20pm",
        ),
        (
            TaskFrequency(
                amount=1,
                type=FrequencyType.per,
                period=FrequencyPeriod.week,
                once_per_weekday=Weekday.monday,
            ),
            "Once per week on monday at any time",
        ),
        (
            TaskFrequency(
                amount=1,
                type=FrequencyType.per,
                period=FrequencyPeriod.week,
                once_at_time=time(12, 20),
            ),
            "Once per week on any day at 12:20pm",
        ),
        (
            TaskFrequency(
                amount=1,
                type=FrequencyType.per,
                period=FrequencyPeriod.week,
                once_per_weekday=Weekday.monday,
                once_at_time=time(11, 20),
            ),
            "Once per week on monday at 11:20am",
        ),
        (
            TaskFrequency(
                amount=2,
                type=FrequencyType.per,
                period=FrequencyPeriod.day,
            ),
            "Twice per day",
        ),
        (
            TaskFrequency(
                amount=3,
                type=FrequencyType.per,
                period=FrequencyPeriod.day,
            ),
            "3 times per day",
        ),
        (
            TaskFrequency(
                amount=2,
                type=FrequencyType.per,
                period=FrequencyPeriod.week,
            ),
            "Twice per week",
        ),
        (
            TaskFrequency(
                amount=2,
                type=FrequencyType.per,
                period=FrequencyPeriod.month,
            ),
            "Twice per month",
        ),
        (
            TaskFrequency(
                amount=2,
                type=FrequencyType.per,
                period=FrequencyPeriod.year,
            ),
            "Twice per year",
        ),
    ],
)
def test_task_frequency_representation(frequency, expected_representation):
    assert frequency.representation == expected_representation
