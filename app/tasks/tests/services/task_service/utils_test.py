from datetime import date, datetime, time
from typing import List, Optional, Union

import pytest

from app.tasks.models.task import TaskStatus
from app.tasks.models.task_frequency import FrequencyPeriod, FrequencyType, Weekday
from app.tasks.models.task_until import UntilType
from app.tasks.services.task_service._utils import (
    compute_approximated_next_event_datetime,
    compute_task_status,
    get_end_of_current_period,
)
from app.tasks.tests.factories import (
    TaskEventFactory,
    TaskFactory,
    TaskFrequencyFactory,
)


@pytest.mark.parametrize(
    "period, current_date, expected_datetime",
    [
        # Day
        (FrequencyPeriod.day, date(2020, 12, 25), datetime(2020, 12, 25, 23, 59)),
        # Week - Start of week
        (FrequencyPeriod.week, date(2024, 7, 1), datetime(2024, 7, 7, 23, 59)),
        # Week - Mid week
        (FrequencyPeriod.week, date(2024, 7, 4), datetime(2024, 7, 7, 23, 59)),
        # Week - End of week
        (FrequencyPeriod.week, date(2024, 7, 7), datetime(2024, 7, 7, 23, 59)),
        # Month - Start of month (31 day month)
        (FrequencyPeriod.month, date(2024, 7, 1), datetime(2024, 7, 31, 23, 59)),
        # Month - Start of month (29 day month)
        (FrequencyPeriod.month, date(2024, 2, 1), datetime(2024, 2, 29, 23, 59)),
        # Month - Mid month
        (FrequencyPeriod.month, date(2024, 7, 13), datetime(2024, 7, 31, 23, 59)),
        # Month - End of month
        (FrequencyPeriod.month, date(2024, 7, 31), datetime(2024, 7, 31, 23, 59)),
        # Year - Start of year
        (FrequencyPeriod.year, date(2024, 1, 1), datetime(2024, 12, 31, 23, 59)),
        # Year - Mid year
        (FrequencyPeriod.year, date(2024, 7, 1), datetime(2024, 12, 31, 23, 59)),
        # Year - End of year
        (FrequencyPeriod.year, date(2024, 12, 31), datetime(2024, 12, 31, 23, 59)),
    ],
)
def test_get_end_of_current_period(period, current_date, expected_datetime):
    end_of_period = get_end_of_current_period(period=period, current_date=current_date)
    assert end_of_period == expected_datetime


@pytest.mark.parametrize(
    "desc,task_factory,optional_previous_event_datetimes,expected_next_event_datetime",
    [
        (
            "On - already done",
            lambda: TaskFactory(
                frequency=TaskFrequencyFactory(
                    type=FrequencyType.on,
                    once_on_date=date(2020, 12, 25),
                )
            ),
            datetime(2020, 12, 25, 12, 0, 0),
            None,
        ),
        (
            "On - date",
            lambda: TaskFactory(
                frequency=TaskFrequencyFactory(
                    type=FrequencyType.on,
                    once_on_date=date(2020, 12, 25),
                )
            ),
            None,
            datetime(2020, 12, 25, 23, 59, 0),
        ),
        (
            "On - date and time",
            lambda: TaskFactory(
                frequency=TaskFrequencyFactory(
                    type=FrequencyType.on,
                    once_on_date=date(2020, 12, 25),
                    once_at_time=time(12, 20),
                )
            ),
            None,
            datetime(2020, 12, 25, 12, 20, 0),
        ),
        (
            "This - already completed",
            lambda: TaskFactory(
                created=datetime(2020, 12, 25, 12, 0, 0),
                frequency=TaskFrequencyFactory(
                    type=FrequencyType.this,
                    period=FrequencyPeriod.day,
                    amount=1,
                    use_calendar_period=True,
                ),
            ),
            datetime(2020, 12, 25, 12, 0, 0),
            None,
        ),
        (
            "This - just created - once this calendar day",
            lambda: TaskFactory(
                created=datetime(2020, 12, 25, 12, 0, 0),
                frequency=TaskFrequencyFactory(
                    type=FrequencyType.this,
                    period=FrequencyPeriod.day,
                    amount=1,
                    use_calendar_period=True,
                ),
            ),
            None,
            datetime(2020, 12, 25, 17, 59, 0),
        ),
        (
            "This - just created - twice this calendar day",
            lambda: TaskFactory(
                created=datetime(2020, 12, 25, 12, 0, 0),
                frequency=TaskFrequencyFactory(
                    type=FrequencyType.this,
                    period=FrequencyPeriod.day,
                    amount=2,
                    use_calendar_period=True,
                ),
            ),
            None,
            datetime(2020, 12, 25, 15, 59, 0),
        ),
        (
            "This - with previous event - twice this calendar day",
            lambda: TaskFactory(
                created=datetime(2020, 12, 25, 9, 0, 0),
                frequency=TaskFrequencyFactory(
                    type=FrequencyType.this,
                    period=FrequencyPeriod.day,
                    amount=2,
                    use_calendar_period=True,
                ),
            ),
            datetime(2020, 12, 25, 10, 0, 0),
            datetime(2020, 12, 25, 16, 59, 0),
        ),
        (
            "This - just created - once this calendar week",
            lambda: TaskFactory(
                created=datetime(2024, 7, 2, 12, 0, 0),  # Tues
                frequency=TaskFrequencyFactory(
                    type=FrequencyType.this,
                    period=FrequencyPeriod.week,
                    amount=1,
                    use_calendar_period=True,
                ),
            ),
            None,
            datetime(
                2024, 7, 5, 5, 59, 0
            ),  # Fri (half way through whats left of the week)
        ),
        (
            "This - just created - twice this calendar week",
            lambda: TaskFactory(
                created=datetime(2024, 7, 2, 12, 0, 0),  # Mon
                frequency=TaskFrequencyFactory(
                    type=FrequencyType.this,
                    period=FrequencyPeriod.week,
                    amount=2,
                    use_calendar_period=True,
                ),
            ),
            None,
            datetime(2024, 7, 4, 7, 59, 0),  # Thurs
        ),
        (
            "This - with previous event - twice this calendar week",
            lambda: TaskFactory(
                created=datetime(2024, 7, 2, 12, 0, 0),  # Mon
                frequency=TaskFrequencyFactory(
                    type=FrequencyType.this,
                    period=FrequencyPeriod.week,
                    amount=2,
                    use_calendar_period=True,
                ),
            ),
            datetime(2024, 7, 4, 7, 59, 0),  # Thurs
            datetime(2024, 7, 6, 3, 59, 0),  # Saturday
        ),
        (
            "This - just created - once this calendar month",
            lambda: TaskFactory(
                created=datetime(2024, 7, 10, 12, 0, 0),
                frequency=TaskFrequencyFactory(
                    type=FrequencyType.this,
                    period=FrequencyPeriod.month,
                    amount=1,
                    use_calendar_period=True,
                ),
            ),
            None,
            datetime(2024, 7, 21, 5, 59, 0),
        ),
        (
            "This - just created - twice this calendar month",
            lambda: TaskFactory(
                created=datetime(2024, 7, 10, 12, 0, 0),
                frequency=TaskFrequencyFactory(
                    type=FrequencyType.this,
                    period=FrequencyPeriod.month,
                    amount=2,
                    use_calendar_period=True,
                ),
            ),
            None,
            datetime(2024, 7, 17, 15, 59, 0),
        ),
        (
            "This - with previous event - twice this calendar month",
            lambda: TaskFactory(
                created=datetime(2024, 7, 10, 12, 0, 0),
                frequency=TaskFrequencyFactory(
                    type=FrequencyType.this,
                    period=FrequencyPeriod.month,
                    amount=2,
                    use_calendar_period=True,
                ),
            ),
            datetime(2024, 7, 17, 15, 59, 0),
            datetime(2024, 7, 24, 19, 59, 0),
        ),
        (
            "This - just created - once this calendar year",
            lambda: TaskFactory(
                created=datetime(2024, 2, 10, 12, 0, 0),
                frequency=TaskFrequencyFactory(
                    type=FrequencyType.this,
                    period=FrequencyPeriod.year,
                    amount=1,
                    use_calendar_period=True,
                ),
            ),
            None,
            datetime(2024, 7, 22, 5, 59, 0),
        ),
        (
            "This - just created - twice this calendar year",
            lambda: TaskFactory(
                created=datetime(2024, 2, 10, 12, 0, 0),
                frequency=TaskFrequencyFactory(
                    type=FrequencyType.this,
                    period=FrequencyPeriod.year,
                    amount=2,
                    use_calendar_period=True,
                ),
            ),
            None,
            datetime(2024, 5, 28, 23, 59, 0),
        ),
        (
            "This - with previous event - twice this calendar year",
            lambda: TaskFactory(
                created=datetime(2024, 2, 10, 12, 0, 0),
                frequency=TaskFrequencyFactory(
                    type=FrequencyType.this,
                    period=FrequencyPeriod.year,
                    amount=2,
                    use_calendar_period=True,
                ),
            ),
            datetime(2024, 5, 28, 23, 59, 0),
            datetime(2024, 9, 14, 11, 59, 0),
        ),
        (
            "This - just created - once this rolling calendar day",
            lambda: TaskFactory(
                created=datetime(2024, 2, 10, 12, 0, 0),
                frequency=TaskFrequencyFactory(
                    type=FrequencyType.this,
                    period=FrequencyPeriod.day,
                    amount=1,
                    use_calendar_period=False,
                ),
            ),
            None,
            datetime(2024, 2, 11, 0, 0, 0),
        ),
        (
            "This - just created - twice this rolling calendar day",
            lambda: TaskFactory(
                created=datetime(2024, 2, 10, 12, 0, 0),
                frequency=TaskFrequencyFactory(
                    type=FrequencyType.this,
                    period=FrequencyPeriod.day,
                    amount=2,
                    use_calendar_period=False,
                ),
            ),
            None,
            datetime(2024, 2, 10, 20, 0, 0),
        ),
        (
            "This - with previous event - twice this rolling calendar day",
            lambda: TaskFactory(
                created=datetime(2024, 2, 10, 12, 0, 0),
                frequency=TaskFrequencyFactory(
                    type=FrequencyType.this,
                    period=FrequencyPeriod.day,
                    amount=2,
                    use_calendar_period=False,
                ),
            ),
            datetime(2024, 2, 10, 20, 0, 0),
            datetime(2024, 2, 11, 4, 0, 0),
        ),
        (
            "This - just created - once this rolling calendar week",
            lambda: TaskFactory(
                created=datetime(2024, 7, 5, 12, 0, 0),  # Friday
                frequency=TaskFrequencyFactory(
                    type=FrequencyType.this,
                    period=FrequencyPeriod.week,
                    amount=1,
                    use_calendar_period=False,
                ),
            ),
            None,
            datetime(2024, 7, 9, 0, 0, 0),  # Tuesday
        ),
        (
            "This - just created - twice this rolling calendar week",
            lambda: TaskFactory(
                created=datetime(2024, 7, 5, 12, 0, 0),  # Friday
                frequency=TaskFrequencyFactory(
                    type=FrequencyType.this,
                    period=FrequencyPeriod.week,
                    amount=2,
                    use_calendar_period=False,
                ),
            ),
            None,
            datetime(2024, 7, 7, 20, 0, 0),  # Sunday
        ),
        (
            "This - with previous event - twice this rolling calendar week",
            lambda: TaskFactory(
                created=datetime(2024, 7, 5, 12, 0, 0),  # Friday
                frequency=TaskFrequencyFactory(
                    type=FrequencyType.this,
                    period=FrequencyPeriod.week,
                    amount=2,
                    use_calendar_period=False,
                ),
            ),
            datetime(2024, 7, 7, 20, 0, 0),  # Sunday
            datetime(2024, 7, 10, 4, 0, 0),  # Wednesday
        ),
        (
            "This - just created - once this rolling calendar month",
            lambda: TaskFactory(
                created=datetime(2024, 7, 20, 12, 0, 0),
                frequency=TaskFrequencyFactory(
                    type=FrequencyType.this,
                    period=FrequencyPeriod.month,
                    amount=1,
                    use_calendar_period=False,
                ),
            ),
            None,
            datetime(2024, 8, 4, 12, 0, 0),
        ),
        (
            "This - just created - twice this rolling calendar month",
            lambda: TaskFactory(
                created=datetime(2024, 7, 20, 12, 0, 0),
                frequency=TaskFrequencyFactory(
                    type=FrequencyType.this,
                    period=FrequencyPeriod.month,
                    amount=2,
                    use_calendar_period=False,
                ),
            ),
            None,
            datetime(2024, 7, 30, 12, 0, 0),
        ),
        (
            "This - with previous event - twice this rolling calendar month",
            lambda: TaskFactory(
                created=datetime(2024, 7, 20, 12, 0, 0),
                frequency=TaskFrequencyFactory(
                    type=FrequencyType.this,
                    period=FrequencyPeriod.month,
                    amount=2,
                    use_calendar_period=False,
                ),
            ),
            datetime(2024, 7, 30, 12, 0, 0),
            datetime(2024, 8, 9, 12, 0, 0),
        ),
        (
            "This - just created - once this rolling calendar year",
            lambda: TaskFactory(
                created=datetime(2024, 10, 1, 12, 0, 0),
                frequency=TaskFrequencyFactory(
                    type=FrequencyType.this,
                    period=FrequencyPeriod.year,
                    amount=1,
                    use_calendar_period=False,
                ),
            ),
            None,
            datetime(2025, 4, 2, 0, 0, 0),
        ),
        (
            "This - just created - twice this rolling calendar year",
            lambda: TaskFactory(
                created=datetime(2024, 10, 1, 12, 0, 0),
                frequency=TaskFrequencyFactory(
                    type=FrequencyType.this,
                    period=FrequencyPeriod.year,
                    amount=2,
                    use_calendar_period=False,
                ),
            ),
            None,
            datetime(2025, 1, 31, 4, 0, 0),
        ),
        (
            "This - with previous event - twice this rolling calendar year",
            lambda: TaskFactory(
                created=datetime(2024, 10, 1, 12, 0, 0),
                frequency=TaskFrequencyFactory(
                    type=FrequencyType.this,
                    period=FrequencyPeriod.year,
                    amount=2,
                    use_calendar_period=False,
                ),
            ),
            datetime(2025, 1, 31, 4, 0, 0),
            datetime(2025, 6, 1, 20, 0, 0),
        ),
        (
            "Per - once per day - just created - no specific time",
            lambda: TaskFactory(
                created=datetime(2024, 10, 1, 12, 0, 0),
                frequency=TaskFrequencyFactory(
                    type=FrequencyType.per,
                    period=FrequencyPeriod.day,
                    amount=1,
                ),
            ),
            None,
            datetime(2024, 10, 1, 12, 0, 0),
        ),
        (
            "Per - once per day - just created - with specific time",
            lambda: TaskFactory(
                created=datetime(2024, 10, 1, 12, 0, 0),
                frequency=TaskFrequencyFactory(
                    type=FrequencyType.per,
                    period=FrequencyPeriod.day,
                    once_at_time=time(11, 0),
                    amount=1,
                ),
            ),
            None,
            datetime(2024, 10, 1, 11, 0, 0),
        ),
        (
            "Per - once per day - with previous event - no specific time",
            lambda: TaskFactory(
                created=datetime(2024, 10, 1, 12, 0, 0),
                frequency=TaskFrequencyFactory(
                    type=FrequencyType.per,
                    period=FrequencyPeriod.day,
                    amount=1,
                ),
            ),
            datetime(2024, 11, 12, 11, 0, 0),
            datetime(2024, 11, 13, 12, 0, 0),
        ),
        (
            "Per - once per day - with previous event - with specific time",
            lambda: TaskFactory(
                created=datetime(2024, 10, 1, 12, 0, 0),
                frequency=TaskFrequencyFactory(
                    type=FrequencyType.per,
                    period=FrequencyPeriod.day,
                    once_at_time=time(14, 0),
                    amount=1,
                ),
            ),
            datetime(2024, 11, 12, 11, 0, 0),
            datetime(2024, 11, 13, 14, 0, 0),
        ),
        (
            "Per - once per specific weekday - just created - day before weekday",
            lambda: TaskFactory(
                created=datetime(2024, 7, 5, 11, 0, 0),  # Friday
                frequency=TaskFrequencyFactory(
                    type=FrequencyType.per,
                    period=FrequencyPeriod.week,
                    once_per_weekday=Weekday.saturday,
                    amount=1,
                ),
            ),
            None,
            datetime(2024, 7, 6, 12, 0, 0),
        ),
        (
            "Per - once per specific weekday - just created - day before weekday - at specific time",
            lambda: TaskFactory(
                created=datetime(2024, 7, 5, 11, 0, 0),  # Friday
                frequency=TaskFrequencyFactory(
                    type=FrequencyType.per,
                    period=FrequencyPeriod.week,
                    once_per_weekday=Weekday.saturday,
                    once_at_time=time(16, 0),
                    amount=1,
                ),
            ),
            None,
            datetime(2024, 7, 6, 16, 0, 0),
        ),
        (
            "Per - once per specific weekday - just created - day of weekday",
            lambda: TaskFactory(
                created=datetime(2024, 7, 5, 11, 0, 0),  # Friday
                frequency=TaskFrequencyFactory(
                    type=FrequencyType.per,
                    period=FrequencyPeriod.week,
                    once_per_weekday=Weekday.friday,
                    amount=1,
                ),
            ),
            None,
            datetime(2024, 7, 5, 12, 0, 0),
        ),
        (
            "Per - once per specific weekday - just created - day after weekday",
            lambda: TaskFactory(
                created=datetime(2024, 7, 5, 11, 0, 0),  # Friday
                frequency=TaskFrequencyFactory(
                    type=FrequencyType.per,
                    period=FrequencyPeriod.week,
                    once_per_weekday=Weekday.thursday,
                    amount=1,
                ),
            ),
            None,
            datetime(2024, 7, 11, 12, 0, 0),  # Next thursday
        ),
        (
            "Per - once per specific weekday - with previous event - day before weekday",
            lambda: TaskFactory(
                created=datetime(2024, 7, 2, 11, 0, 0),  # Tues
                frequency=TaskFrequencyFactory(
                    type=FrequencyType.per,
                    period=FrequencyPeriod.week,
                    once_per_weekday=Weekday.thursday,
                    amount=1,
                ),
            ),
            datetime(2024, 7, 3, 10, 0, 0),  # Weds
            datetime(2024, 7, 4, 12, 0, 0),  # Thurs
        ),
        (
            "Per - once per specific weekday - with previous event - day of weekday",
            lambda: TaskFactory(
                created=datetime(2024, 7, 2, 11, 0, 0),  # Tues
                frequency=TaskFrequencyFactory(
                    type=FrequencyType.per,
                    period=FrequencyPeriod.week,
                    once_per_weekday=Weekday.thursday,
                    amount=1,
                ),
            ),
            datetime(2024, 7, 4, 10, 0, 0),  # Thurs
            datetime(2024, 7, 11, 12, 0, 0),  # Next Thurs
        ),
        (
            "Per - once per specific weekday - with previous event - day after weekday",
            lambda: TaskFactory(
                created=datetime(2024, 7, 2, 11, 0, 0),  # Tues
                frequency=TaskFrequencyFactory(
                    type=FrequencyType.per,
                    period=FrequencyPeriod.week,
                    once_per_weekday=Weekday.thursday,
                    amount=1,
                ),
            ),
            datetime(2024, 7, 5, 10, 0, 0),  # Fri
            datetime(2024, 7, 11, 12, 0, 0),  # Next Thurs
        ),
        (
            "Per - multiple - just created - five times per week",
            lambda: TaskFactory(
                created=datetime(2024, 7, 2, 11, 0, 0),  # Tues
                frequency=TaskFrequencyFactory(
                    type=FrequencyType.per,
                    period=FrequencyPeriod.week,
                    amount=5,
                ),
            ),
            None,
            datetime(2024, 7, 3, 20, 36, 0),  # Later on weds
        ),
        (
            "Per - multiple - with previous - four times per month",
            lambda: TaskFactory(
                created=datetime(2023, 7, 15, 11, 0, 0),
                frequency=TaskFrequencyFactory(
                    type=FrequencyType.per,
                    period=FrequencyPeriod.month,
                    amount=4,
                ),
            ),
            datetime(2024, 7, 15, 11, 0, 0),
            datetime(2024, 7, 22, 23, 0, 0),
        ),
        (
            "Per - multiple - with two previous - second latest out of scope",
            lambda: TaskFactory(
                created=datetime(2023, 7, 15, 11, 0, 0),
                frequency=TaskFrequencyFactory(
                    type=FrequencyType.per,
                    period=FrequencyPeriod.month,
                    amount=4,
                ),
            ),
            [datetime(2024, 7, 15, 11, 0, 0), datetime(2024, 6, 22, 23, 0, 0)],
            datetime(2024, 7, 22, 23, 0, 0),
        ),
        (
            "Per - multiple - with two previous - second latest in scope",
            lambda: TaskFactory(
                created=datetime(2023, 7, 15, 11, 0, 0),
                frequency=TaskFrequencyFactory(
                    type=FrequencyType.per,
                    period=FrequencyPeriod.month,
                    amount=4,
                ),
            ),
            [datetime(2024, 7, 15, 11, 0, 0), datetime(2024, 7, 14, 12, 0, 0)],
            datetime(2024, 7, 26, 5, 30, 0),
        ),
    ],
)
def test_compute_approximated_next_event_datetime(
    desc,
    task_factory,
    optional_previous_event_datetimes: Optional[Union[datetime, List[datetime]]],
    expected_next_event_datetime,
    session,
):
    task = task_factory()
    if optional_previous_event_datetimes:
        for optional_previous_event_datetime in (
            optional_previous_event_datetimes
            if isinstance(optional_previous_event_datetimes, list)
            else [optional_previous_event_datetimes]
        ):
            TaskEventFactory(
                task=task, effective_datetime=optional_previous_event_datetime
            )
    computed = compute_approximated_next_event_datetime(task=task)
    assert computed == expected_next_event_datetime


@pytest.mark.parametrize(
    "desc,task_factory,optional_events_count,optional_now_datetime,expected_status",
    [
        (
            "Amount - Amount not reached",
            lambda: TaskFactory(
                status=TaskStatus.ongoing,
                until__type=UntilType.amount,
                until__amount=2,
            ),
            1,
            None,
            TaskStatus.ongoing,
        ),
        (
            "Amount - Amount not reached but manually completed",
            lambda: TaskFactory(
                status=TaskStatus.completed,
                manually_completed_at=datetime(2020, 12, 25, 12, 0, 0),
                until__type=UntilType.amount,
                until__amount=2,
            ),
            1,
            None,
            TaskStatus.completed,
        ),
        (
            "Amount - Amount not reached but paused",
            lambda: TaskFactory(
                status=TaskStatus.paused,
                until__type=UntilType.amount,
                until__amount=2,
            ),
            1,
            None,
            TaskStatus.paused,
        ),
        (
            "Amount - Amount reached",
            lambda: TaskFactory(
                status=TaskStatus.ongoing,
                until__type=UntilType.amount,
                until__amount=2,
            ),
            2,
            None,
            TaskStatus.completed,
        ),
        (
            "Amount - Amount exceeded",
            lambda: TaskFactory(
                status=TaskStatus.ongoing,
                until__type=UntilType.amount,
                until__amount=2,
            ),
            3,
            None,
            TaskStatus.completed,
        ),
        (
            "Date - Date not reached",
            lambda: TaskFactory(
                status=TaskStatus.ongoing,
                until__type=UntilType.date,
                until__date=date(2025, 12, 20),
            ),
            None,
            date(2024, 12, 20),
            TaskStatus.ongoing,
        ),
        (
            "Date - Date not reached but manually completed",
            lambda: TaskFactory(
                status=TaskStatus.ongoing,
                until__type=UntilType.date,
                until__date=date(2025, 12, 20),
                manually_completed_at=datetime(2024, 12, 25, 12, 0, 0),
            ),
            None,
            date(2024, 12, 20),
            TaskStatus.completed,
        ),
        (
            "Date - Date not reached but paused",
            lambda: TaskFactory(
                status=TaskStatus.paused,
                until__type=UntilType.date,
                until__date=date(2025, 12, 20),
            ),
            None,
            date(2024, 12, 20),
            TaskStatus.paused,
        ),
        (
            "Date - Date reached",
            lambda: TaskFactory(
                status=TaskStatus.ongoing,
                until__type=UntilType.date,
                until__date=date(2025, 12, 20),
            ),
            None,
            date(2025, 12, 20),
            TaskStatus.completed,
        ),
        (
            "Date - Date exceeded",
            lambda: TaskFactory(
                status=TaskStatus.ongoing,
                until__type=UntilType.date,
                until__date=date(2025, 12, 20),
            ),
            None,
            date(2026, 12, 20),
            TaskStatus.completed,
        ),
        (
            "Stopped - Not completed",
            lambda: TaskFactory(
                status=TaskStatus.ongoing,
                until__type=UntilType.stopped,
            ),
            None,
            None,
            TaskStatus.ongoing,
        ),
        (
            "Stopped - Manually completed",
            lambda: TaskFactory(
                status=TaskStatus.completed,
                until__type=UntilType.stopped,
                manually_completed_at=datetime(2024, 12, 25, 12, 0, 0),
            ),
            None,
            None,
            TaskStatus.completed,
        ),
        (
            "Completed - Not completed",
            lambda: TaskFactory(
                status=TaskStatus.ongoing,
                until__type=UntilType.completed,
            ),
            None,
            None,
            TaskStatus.ongoing,
        ),
        (
            "Completed - Manually completed",
            lambda: TaskFactory(
                status=TaskStatus.completed,
                until__type=UntilType.completed,
                manually_completed_at=datetime(2024, 12, 25, 12, 0, 0),
            ),
            None,
            None,
            TaskStatus.completed,
        ),
    ],
)
def test_compute_task_status(
    desc,
    task_factory,
    optional_events_count,
    optional_now_datetime,
    expected_status,
    session,
):
    task = task_factory()
    if optional_events_count:
        TaskEventFactory.create_batch(optional_events_count, task=task)

    status = compute_task_status(
        task=task, now=optional_now_datetime or datetime.utcnow()
    )

    assert status == expected_status
