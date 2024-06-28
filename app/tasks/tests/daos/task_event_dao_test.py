from datetime import datetime

from app.accounts.tests.factories import UserFactory
from app.tasks.daos.task_event_dao import TaskEventDao
from app.tasks.models.task_event import TaskEvent, TaskEventAround
from app.tasks.tests.factories import TaskEventFactory, TaskFactory


def test_create_event_ok(session):
    task = TaskFactory()

    task_event = TaskEventDao(session=session).create(
        task_id=task.id,
        around=TaskEventAround.specifically,
        at=datetime(2020, 12, 25, 12, 0, 0),
    )

    assert task_event.task == task
    assert task_event.around == TaskEventAround.specifically
    assert task_event.at == datetime(2020, 12, 25, 12, 0, 0)


def test_query_filter_by_id(session, subtests):
    # Noise
    TaskFactory.create_batch(2)

    task_event_1 = TaskEventFactory()
    task_event_2 = TaskEventFactory()

    cases = [
        ({}, [task_event_1, task_event_2]),
        ({"id": task_event_1.id}, [task_event_1]),
    ]

    for filters, expected_task_events in cases:
        with subtests.test():
            task_events = TaskEventDao(session=session).list(**filters)
            assert task_events == expected_task_events


def test_query_filter_by_task_id(session, subtests):
    # Noise
    TaskFactory.create_batch(3)

    task_event_1 = TaskEventFactory()
    task_event_2 = TaskEventFactory()

    cases = [
        ({}, [task_event_1, task_event_2]),
        ({"task_id": task_event_1.task_id}, [task_event_1]),
    ]

    for filters, expected_task_events in cases:
        with subtests.test():
            task_events = TaskEventDao(session=session).list(**filters)
            assert task_events == expected_task_events


def test_query_filter_by_user_id(session, subtests):
    # Noise
    TaskFactory.create_batch(3)
    UserFactory.create_batch(4)

    task_event_1 = TaskEventFactory()
    task_event_2 = TaskEventFactory()

    cases = [
        ({}, [task_event_1, task_event_2]),
        ({"user_id": task_event_1.task.user_id}, [task_event_1]),
    ]

    for filters, expected_task_events in cases:
        with subtests.test():
            task_events = TaskEventDao(session=session).list(**filters)
            assert task_events == expected_task_events


def test_delete_ok(session):
    task_event = TaskEventFactory()

    TaskEventDao(session=session).delete(
        id=task_event.id, user_id=task_event.task.user_id
    )

    assert session.get(TaskEvent, task_event.id) is None
