from datetime import time

import pytest
from sqlalchemy.exc import NoResultFound

from app.accounts.tests.factories import UserFactory
from app.tasks.models.task import TaskStatus
from app.tasks.models.task_frequency import (
    FrequencyPeriod,
    FrequencyType,
    Weekday,
)
from app.tasks.models.task_until import UntilType
from app.tasks.schemas.task_schema import (
    TaskCreationSchema,
    TaskFrequencyCreationSchema,
    TaskUntilCreationSchema,
)
from app.tasks.services import task_service
from app.tasks.tests.factories import CategoryFactory, TaskFactory


def test_create_task_ok__per__once_per_period_until_stopped(session):
    user = UserFactory()
    category = CategoryFactory(user=user)
    other_task = TaskFactory()  # Noise

    task = task_service.create_task(
        new_task=TaskCreationSchema(
            name=other_task.name,
            description="mydescription",
            category_id=category.id,
            frequency=TaskFrequencyCreationSchema(
                type=FrequencyType.per,
                amount=1,
                period=FrequencyPeriod.quarter,
            ),
            until=TaskUntilCreationSchema(type=UntilType.stopped),
        ),
        authenticated_user=user,
        session=session,
    )

    assert task.name == other_task.name
    assert task.category == category
    assert task.description == "mydescription"
    assert task.user == user
    assert task.until.type == UntilType.stopped
    assert task.frequency.type == FrequencyType.per
    assert task.frequency.amount == 1
    assert task.frequency.period == FrequencyPeriod.quarter


def test_create_task_ok__per__once_per_week_on_weekday_until_stopped(session):
    user = UserFactory()
    category = CategoryFactory(user=user)
    other_task = TaskFactory()  # Noise

    task = task_service.create_task(
        new_task=TaskCreationSchema(
            name=other_task.name,
            description="mydescription",
            category_id=category.id,
            frequency=TaskFrequencyCreationSchema(
                type=FrequencyType.per,
                amount=1,
                period=FrequencyPeriod.week,
                once_per_weekday=Weekday.friday,
                once_at_time=time(12, 0, 0),
            ),
            until=TaskUntilCreationSchema(type=UntilType.stopped),
        ),
        authenticated_user=user,
        session=session,
    )

    assert task.name == other_task.name
    assert task.category == category
    assert task.description == "mydescription"
    assert task.user == user
    assert task.until.type == UntilType.stopped
    assert task.frequency.type == FrequencyType.per
    assert task.frequency.amount == 1
    assert task.frequency.period == FrequencyPeriod.week
    assert task.frequency.once_per_weekday == Weekday.friday
    assert task.frequency.once_at_time == time(12, 0, 0)


def test_create_task_failure_category_not_visible(session):
    category = CategoryFactory()
    user = UserFactory()

    with pytest.raises(NoResultFound):
        task_service.create_task(
            new_task=TaskCreationSchema(
                name="mytask",
                description="mydescription",
                category_id=category.id,
                frequency=TaskFrequencyCreationSchema(
                    type=FrequencyType.per,
                    amount=1,
                    period=FrequencyPeriod.quarter,
                ),
                until=TaskUntilCreationSchema(type=UntilType.completed),
            ),
            authenticated_user=user,
            session=session,
        )


def test_create_task_failure_duplicate_name(session):
    user = UserFactory()
    task = TaskFactory(user=user)

    with pytest.raises(ValueError) as ctx:
        task_service.create_task(
            new_task=TaskCreationSchema(
                name=task.name,
                description="mydescription",
                frequency=TaskFrequencyCreationSchema(
                    type=FrequencyType.per,
                    amount=1,
                    period=FrequencyPeriod.quarter,
                ),
                until=TaskUntilCreationSchema(type=UntilType.completed),
            ),
            authenticated_user=user,
            session=session,
        )

    assert ctx.value.args[0] == "A task already exists with this name"


def test_get_task_ok(session):
    task = TaskFactory()
    task_service.get_task(
        task_id=task.id,
        authenticated_user=task.user,
        session=session,
    )


def test_get_task_failure_invalid_id(session):
    with pytest.raises(NoResultFound):
        task_service.get_task(
            task_id=1234,
            authenticated_user=UserFactory(),
            session=session,
        )


def test_get_task_failure_not_visible_to_user(session):
    task = TaskFactory()

    with pytest.raises(NoResultFound):
        task_service.get_task(
            task_id=task.id,
            authenticated_user=UserFactory(),
            session=session,
        )


def test_get_tasks_ok(session):
    task_1 = TaskFactory()
    task_2 = TaskFactory(user=task_1.user)
    task_3 = TaskFactory()  # Noise

    tasks = task_service.get_tasks(
        session=session,
        authenticated_user=task_1.user,
    )

    assert tasks == [task_1, task_2]


def test_get_tasks_filter_status(session, subtests):
    # Noise
    TaskFactory()

    user = UserFactory()
    task_1 = TaskFactory(user=user, status=TaskStatus.ongoing)
    task_2 = TaskFactory(user=user, status=TaskStatus.paused)
    task_3 = TaskFactory(user=user, status=TaskStatus.completed)

    cases = [
        (TaskStatus.ongoing, [task_1]),
        (TaskStatus.paused, [task_2]),
        (TaskStatus.completed, [task_3]),
    ]

    for status, expected_tasks in cases:
        with subtests.test():
            tasks = task_service.get_tasks(
                session=session,
                authenticated_user=task_1.user,
                status=status,
            )

            assert tasks == expected_tasks


def test_get_tasks_filter_category_id(session, subtests):
    # Noise
    TaskFactory()

    user = UserFactory()
    category = CategoryFactory(user=user)
    task_1 = TaskFactory(user=user, category=category)
    task_2 = TaskFactory(user=user)

    cases = [
        (category.id, [task_1]),
        (None, [task_2]),
    ]

    for category_id, expected_tasks in cases:
        with subtests.test():
            tasks = task_service.get_tasks(
                session=session,
                authenticated_user=task_1.user,
                category_id=category_id,
            )

            assert tasks == expected_tasks


def test_pause_task_ok(session):
    task = TaskFactory(status=TaskStatus.ongoing)

    task_service.pause_task(
        authenticated_user=task.user,
        task_id=task.id,
        session=session,
    )

    session.refresh(task)
    assert task.status == TaskStatus.paused


def test_pause_task_failure_not_visible_to_user(session):
    task = TaskFactory(status=TaskStatus.ongoing)

    with pytest.raises(NoResultFound):
        task_service.pause_task(
            authenticated_user=UserFactory(),
            task_id=task.id,
            session=session,
        )


def test_pause_task_failure_task_not_ongoing(session):
    task = TaskFactory(status=TaskStatus.completed)

    with pytest.raises(ValueError) as ctx:
        task_service.pause_task(
            authenticated_user=task.user,
            task_id=task.id,
            session=session,
        )

    assert ctx.value.args[0] == "Cannot pause a task that isn't ongoing"


def test_complete_task_ok(session):
    task = TaskFactory(status=TaskStatus.ongoing)

    task_service.complete_task(
        authenticated_user=task.user,
        task_id=task.id,
        session=session,
    )

    session.refresh(task)
    assert task.status == TaskStatus.completed


def test_complete_task_failure_not_visible_to_user(session):
    task = TaskFactory(status=TaskStatus.ongoing)

    with pytest.raises(NoResultFound):
        task_service.complete_task(
            authenticated_user=UserFactory(),
            task_id=task.id,
            session=session,
        )


def test_complete_task_failure_task_not_ongoing(session):
    task = TaskFactory(status=TaskStatus.completed)

    with pytest.raises(ValueError) as ctx:
        task_service.complete_task(
            authenticated_user=task.user,
            task_id=task.id,
            session=session,
        )

    assert ctx.value.args[0] == "The task is already completed"
