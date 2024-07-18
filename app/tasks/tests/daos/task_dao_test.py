from datetime import date, datetime, timedelta

import pytest
from sqlalchemy.exc import IntegrityError

from app.accounts.tests.factories import UserFactory
from app.tasks.daos.task_dao import TaskDao
from app.tasks.models.task import Task, TaskStatus
from app.tasks.models.task_until import UntilType
from app.tasks.tests.factories import (
    CategoryFactory,
    TaskFactory,
    TaskFrequencyFactory,
    TaskUntilFactory,
)


def test_create_task_ok(session):
    # Noise
    CategoryFactory.create_batch(1)
    TaskFactory.create_batch(2)
    TaskFrequencyFactory.create_batch(3)
    TaskUntilFactory.create_batch(4)

    # A task with the same name but another user
    existing = TaskFactory()

    user = UserFactory()
    category = CategoryFactory(user=user)
    frequency = TaskFrequencyFactory()
    until = TaskUntilFactory()

    task = TaskDao(session=session).create(
        name=existing.name,
        description="mydesc",
        user_id=user.id,
        category_id=category.id,
        frequency_id=frequency.id,
        until_id=until.id,
    )

    assert task.name == existing.name
    assert task.description == "mydesc"
    assert task.user == user
    assert task.category == category
    assert task.frequency == frequency
    assert task.until == until


def test_create_task_failure_duplicate_name(session):
    existing = TaskFactory()

    user = existing.user
    category = CategoryFactory(user=user)
    frequency = TaskFrequencyFactory()
    until = TaskUntilFactory()

    with pytest.raises(IntegrityError) as ctx:
        TaskDao(session=session).create(
            name=existing.name,
            description="mydesc",
            user_id=user.id,
            category_id=category.id,
            frequency_id=frequency.id,
            until_id=until.id,
        )

    assert "unique_user_task_name" in ctx.value.args[0]


def test_query_default_order_by(session):
    task_0 = TaskFactory(next_event_datetime=None)
    task_1 = TaskFactory(next_event_datetime=datetime(2020, 12, 25, 12, 0, 0))
    task_2 = TaskFactory(next_event_datetime=datetime(2020, 12, 24, 12, 0, 0))
    task_4 = TaskFactory(next_event_datetime=None)

    tasks = TaskDao(session=session).list()
    assert tasks == [task_2, task_1, task_0, task_4]


def test_query_filter_by_name(session, subtests):
    task_1 = TaskFactory()
    task_2 = TaskFactory()

    cases = [
        ({}, [task_1, task_2]),
        ({"name": task_1.name}, [task_1]),
        ({"name": task_2.name}, [task_2]),
    ]

    for filters, expected_tasks in cases:
        with subtests.test():
            tasks = TaskDao(session=session).list(**filters)
            assert tasks == expected_tasks


def test_query_filter_by_id(session, subtests):
    task_1 = TaskFactory()
    task_2 = TaskFactory()

    cases = [
        ({}, [task_1, task_2]),
        ({"id": task_1.id}, [task_1]),
        ({"id": task_2.id}, [task_2]),
    ]

    for filters, expected_tasks in cases:
        with subtests.test():
            tasks = TaskDao(session=session).list(**filters)
            assert tasks == expected_tasks


def test_query_filter_by_category_id(session, subtests):
    task_1 = TaskFactory(category=None)
    category = CategoryFactory()
    task_2 = TaskFactory(category=category)

    cases = [
        ({}, [task_1, task_2]),
        ({"category_id": None}, [task_1]),
        ({"category_id": category.id}, [task_2]),
    ]

    for filters, expected_tasks in cases:
        with subtests.test():
            tasks = TaskDao(session=session).list(**filters)
            assert tasks == expected_tasks


def test_query_filter_by_status(session, subtests):
    task_1 = TaskFactory(status=TaskStatus.ongoing)
    task_2 = TaskFactory(status=TaskStatus.completed)
    task_3 = TaskFactory(status=TaskStatus.paused)

    cases = [
        ({}, [task_1, task_2, task_3]),
        ({"status": TaskStatus.ongoing}, [task_1]),
        ({"status": TaskStatus.completed}, [task_2]),
        ({"status": TaskStatus.paused}, [task_3]),
    ]

    for filters, expected_tasks in cases:
        with subtests.test():
            tasks = TaskDao(session=session).list(**filters)
            assert tasks == expected_tasks


def test_query_filter_by_user_id(session, subtests):
    # Noise
    UserFactory.create_batch(3)

    task_1 = TaskFactory()
    task_2 = TaskFactory()

    cases = [
        ({}, [task_1, task_2]),
        ({"user_id": task_1.user_id}, [task_1]),
        ({"user_id": task_2.user_id}, [task_2]),
    ]

    for filters, expected_tasks in cases:
        with subtests.test():
            tasks = TaskDao(session=session).list(**filters)
            assert tasks == expected_tasks


def test_update_status_ok(session):
    task = TaskFactory(status=TaskStatus.ongoing)

    TaskDao(session=session).update(
        id=task.id,
        user_id=task.user_id,
        status=TaskStatus.completed,
    )

    session.refresh(task)

    assert task.status == TaskStatus.completed


def test_update_manually_completed_at_ok(session):
    task = TaskFactory(manually_completed_at=None)

    TaskDao(session=session).update(
        id=task.id,
        user_id=task.user_id,
        manually_completed_at=datetime(2012, 12, 25, 12, 0, 0),
    )

    session.refresh(task)

    assert task.manually_completed_at == datetime(2012, 12, 25, 12, 0, 0)


def test_update_next_event_datetime_ok(session):
    task = TaskFactory(next_event_datetime=None)

    TaskDao(session=session).update(
        id=task.id,
        user_id=task.user_id,
        next_event_datetime=datetime(2012, 12, 25, 12, 0, 0),
    )

    session.refresh(task)

    assert task.next_event_datetime == datetime(2012, 12, 25, 12, 0, 0)


def test_update_frequency_id_ok(session):
    task = TaskFactory()
    new_frequency = TaskFrequencyFactory()

    TaskDao(session=session).update(
        id=task.id,
        user_id=task.user_id,
        frequency_id=new_frequency.id,
    )

    session.refresh(task)

    assert task.frequency == new_frequency


def test_update_until_id_ok(session):
    task = TaskFactory()
    new_until = TaskUntilFactory()

    TaskDao(session=session).update(
        id=task.id,
        user_id=task.user_id,
        until_id=new_until.id,
    )

    session.refresh(task)

    assert task.until == new_until


def test_delete_ok(session):
    # Noise
    TaskFactory.create_batch(3)
    UserFactory.create_batch(2)

    task = TaskFactory()

    TaskDao(session=session).delete(id=task.id, user_id=task.user_id)

    assert session.get(Task, task.id) is None


def test_mark_ongoing_date_tasks_as_completed(session):
    to_be_completed_yesterday = TaskFactory(
        status=TaskStatus.ongoing,
        until__type=UntilType.date,
        until__date=date.today() - timedelta(days=1),
    )
    to_be_completed_today__ongoing = TaskFactory(
        status=TaskStatus.ongoing, until__type=UntilType.date, until__date=date.today()
    )
    to_be_completed_today__paused = TaskFactory(
        status=TaskStatus.paused, until__type=UntilType.date, until__date=date.today()
    )
    to_be_completed_tomorrow__ongoing = TaskFactory(
        status=TaskStatus.ongoing,
        until__type=UntilType.date,
        until__date=date.today() + timedelta(days=1),
    )
    to_be_completed_tomorrow__paused = TaskFactory(
        status=TaskStatus.paused,
        until__type=UntilType.date,
        until__date=date.today() + timedelta(days=1),
    )

    TaskDao(session=session).mark_ongoing_date_tasks_as_completed()

    session.refresh(to_be_completed_yesterday)
    session.refresh(to_be_completed_today__ongoing)
    session.refresh(to_be_completed_today__paused)
    session.refresh(to_be_completed_tomorrow__ongoing)
    session.refresh(to_be_completed_tomorrow__paused)

    assert to_be_completed_yesterday.status == TaskStatus.completed
    assert to_be_completed_today__ongoing.status == TaskStatus.completed
    assert to_be_completed_today__paused.status == TaskStatus.completed
    assert to_be_completed_tomorrow__ongoing.status == TaskStatus.ongoing
    assert to_be_completed_tomorrow__paused.status == TaskStatus.paused
