import pytest
from sqlalchemy.exc import IntegrityError

from app.accounts.tests.factories import UserFactory
from app.tasks.daos.task_dao import TaskDao
from app.tasks.models.task import Task, TaskStatus
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


def test_delete_ok(session):
    # Noise
    TaskFactory.create_batch(3)
    UserFactory.create_batch(2)

    task = TaskFactory()

    TaskDao(session=session).delete(id=task.id, user_id=task.user_id)

    assert session.get(Task, task.id) is None
