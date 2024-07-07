import math
import operator
from datetime import date, datetime, time, timedelta
from typing import Callable, Dict, Optional

from app.tasks.models.task import Task, TaskStatus
from app.tasks.models.task_frequency import FrequencyPeriod, FrequencyType, Weekday
from app.tasks.models.task_until import UntilType

period_to_days: Dict[FrequencyPeriod, int] = {
    FrequencyPeriod.day: 1,
    FrequencyPeriod.week: 7,
    FrequencyPeriod.month: 30,  # TODO maybe be more precise depending on month
    FrequencyPeriod.year: 365,
}

weekday_to_int: Dict[Weekday, int] = {
    Weekday.monday: 0,
    Weekday.tuesday: 1,
    Weekday.wednesday: 2,
    Weekday.thursday: 3,
    Weekday.friday: 4,
    Weekday.saturday: 5,
    Weekday.sunday: 6,
}


def get_end_of_current_day(current_date: date) -> datetime:
    return datetime.combine(current_date, time(23, 59))


def get_end_of_current_week(current_date: date) -> datetime:
    return datetime.combine(current_date, time(23, 59)) + timedelta(
        days=6 - current_date.weekday()
    )


def get_end_of_current_month(current_date: date) -> datetime:
    a_few_days_into_next_month = datetime.combine(current_date, time(23, 59)).replace(
        day=28
    ) + timedelta(days=4)
    return a_few_days_into_next_month - timedelta(
        days=a_few_days_into_next_month.date().day
    )


def get_end_of_current_year(current_date: date) -> datetime:
    return datetime(year=current_date.year + 1, month=1, day=1) - timedelta(minutes=1)


period_to_end_of_period: Dict[FrequencyPeriod, Callable] = {
    FrequencyPeriod.day: get_end_of_current_day,
    FrequencyPeriod.week: get_end_of_current_week,
    FrequencyPeriod.month: get_end_of_current_month,
    FrequencyPeriod.year: get_end_of_current_year,
}


def get_end_of_current_period(period: FrequencyPeriod, current_date: date) -> datetime:
    return period_to_end_of_period[period](current_date)


def _compute_approximated_next_event_datetime_for__this(
    task: Task,
) -> Optional[datetime]:
    remaining_events: int = task.frequency.amount - len(task.events)

    if remaining_events < 1:
        # This shouldn't happen because we should validate ongoing status prior to this
        return None

    end_datetime: datetime = (
        get_end_of_current_period(
            period=task.frequency.period, current_date=task.created.date()
        )
        if task.frequency.use_calendar_period
        else (task.created + timedelta(days=period_to_days[task.frequency.period]))
    )

    remaining_minutes: int = (
        end_datetime - (task.latest_event_datetime or task.created)
    ).total_seconds() // 60
    minutes_between_events: int = remaining_minutes // (remaining_events + 1)
    next_event: datetime = (
        task.latest_event.effective_datetime if task.latest_event else task.created
    ) + timedelta(minutes=minutes_between_events)
    return next_event


def _compute_approximated_next_event_datetime_for__on(
    task: Task,
) -> Optional[datetime]:
    """Either the precise date of the event if the time is provided, else
    we choose the end of the day."""
    if len(task.events) > 0:
        # This shouldn't happen because we should validate ongoing status prior to this
        return None

    on_datetime = datetime.combine(task.frequency.once_on_date, time(0, 0))
    on_datetime = on_datetime + (
        timedelta(
            hours=task.frequency.once_at_time.hour,
            minutes=task.frequency.once_at_time.minute,
        )
        if task.frequency.once_at_time
        else timedelta(hours=23, minutes=59)
    )
    return on_datetime


def _compute_approximated_next_event_datetime_for__per(
    task: Task,
) -> datetime:
    latest_event = task.latest_event
    latest_effective_datetime = (
        latest_event.effective_datetime if latest_event else task.created
    )

    if task.frequency.is_once_per_day:
        # Do it the day after the previous event
        # If it hasn't been done, do it today
        next_event_date = (
            (
                datetime.combine(latest_effective_datetime.date(), time())
                + timedelta(days=1)
            ).date()
            if latest_event
            else task.created.date()
        )

        next_event_datetime = datetime.combine(
            next_event_date,
            (
                task.frequency.once_at_time
                if task.frequency.once_at_time
                else time(12, 0)
            ),
        )
        return next_event_datetime

    elif task.frequency.is_once_per_specific_weekday:
        frequency_weekday_int = weekday_to_int[task.frequency.once_per_weekday]
        last_effective_weekday_int = latest_effective_datetime.date().weekday()
        delta_weekdays = last_effective_weekday_int - frequency_weekday_int

        return datetime.combine(
            latest_effective_datetime.date(),
            task.frequency.once_at_time or time(hour=12, minute=0),
        ) + timedelta(
            days=abs(delta_weekdays)
            if (operator.le if not latest_event else operator.lt)(delta_weekdays, 0)
            else (7 - delta_weekdays),
        )
    else:
        # Multiple times per period
        # TODO maybe do minutes between events to support very frequent tasks?
        minutes_between_events = (
            24 * 60 * period_to_days[task.frequency.period]
        ) // task.frequency.amount

        if not latest_event:
            return task.created + timedelta(minutes=minutes_between_events)

        # If there are two recent events, we add allow a bit of a delay before the next required event
        if second_latest_event := task.second_latest_event:
            delta_seconds = (
                latest_event.effective_datetime - second_latest_event.effective_datetime
            ).total_seconds()
            delta_minutes = math.floor(delta_seconds / 60)
            if delta_minutes < minutes_between_events:
                minutes_between_events = minutes_between_events + math.ceil(
                    (minutes_between_events - delta_minutes) / 2
                )

        # This value might be in the past but thats ok, it will be treated as overdue
        return latest_event.effective_datetime + timedelta(
            minutes=minutes_between_events
        )


def compute_approximated_next_event_datetime(task: Task) -> Optional[datetime]:
    if task.status != TaskStatus.ongoing:
        return

    # TODO if the next datetime is after the end date of the task, then
    # it should be None

    return {
        FrequencyType.on: _compute_approximated_next_event_datetime_for__on,
        FrequencyType.per: _compute_approximated_next_event_datetime_for__per,
        FrequencyType.this: _compute_approximated_next_event_datetime_for__this,
    }[task.frequency.type](task=task)


def compute_task_status(task: Task, now: datetime) -> TaskStatus:
    if task.status == TaskStatus.paused:
        return TaskStatus.paused

    if task.manually_completed_at:
        return TaskStatus.completed

    if task.until.type == UntilType.amount:
        return (
            TaskStatus.ongoing
            if len(task.events) < task.until.amount
            else TaskStatus.completed
        )

    if task.until.type == UntilType.date:
        return TaskStatus.ongoing if now < task.until.date else TaskStatus.completed

    return TaskStatus.ongoing
