from datetime import datetime

import pytest
from sqlalchemy.exc import NoResultFound

from app.accounts.tests.factories import UserFactory
from app.tasks.models.task_event import TaskEvent, TaskEventAround
from app.tasks.schemas.task_event_schema import TaskEventCreationSchema
from app.tasks.services.task_event_service.service import (
    create_task_event,
    delete_task_event,
    get_task_event,
    get_task_events,
)
from app.tasks.tests.factories import TaskEventFactory, TaskFactory


def test_create_task_event_ok__today(session):
    user = UserFactory()
    task = TaskFactory(user=user)

    task_event = create_task_event(
        session=session,
        authenticated_user=user,
        task_event_creation_payload=TaskEventCreationSchema(
            task_id=task.id,
            around=TaskEventAround.today,
        ),
    )

    assert task_event.task == task
    assert task_event.around == TaskEventAround.today
    assert task_event.at is None


def test_create_task_event_ok__specifically(session):
    user = UserFactory()
    task = TaskFactory(user=user)

    task_event = create_task_event(
        session=session,
        authenticated_user=user,
        task_event_creation_payload=TaskEventCreationSchema(
            task_id=task.id,
            around=TaskEventAround.specifically,
            at=datetime(2020, 12, 25, 12, 0, 0),
        ),
    )

    assert task_event.task == task
    assert task_event.around == TaskEventAround.specifically
    assert task_event.at == datetime(2020, 12, 25, 12, 0, 0)


def test_create_task_event_failure_task_not_visible_to_user(session):
    user = UserFactory()
    task = TaskFactory()

    with pytest.raises(NoResultFound) as ctx:
        # TODO maybe raise a service validation error instead
        create_task_event(
            session=session,
            authenticated_user=user,
            task_event_creation_payload=TaskEventCreationSchema(
                task_id=task.id,
                around=TaskEventAround.today,
            ),
        )

    assert ctx.value.args[0] == "Task not found"


def test_get_task_event_ok(session):
    task_event = TaskEventFactory()

    retrieved = get_task_event(
        session=session,
        authenticated_user=task_event.task.user,
        task_event_id=task_event.id,
    )

    assert retrieved == task_event


def test_get_task_event_failure_not_visible_to_user(session):
    task_event = TaskEventFactory()

    with pytest.raises(NoResultFound) as ctx:
        get_task_event(
            session=session,
            authenticated_user=UserFactory(),
            task_event_id=task_event.id,
        )

    assert ctx.value.args[0] == "Task Event not found"


def test_get_task_events_ok(session, subtests):
    user_1 = UserFactory()
    task_1 = TaskFactory(user=user_1)
    task_1_event = TaskEventFactory(task=task_1)

    user_2 = UserFactory()
    task_2 = TaskFactory(user=user_2)
    task_2_event = TaskEventFactory(task=task_2)

    cases = [
        ({"task_id": task_1.id, "authenticated_user": user_1}, [task_1_event]),
        ({"task_id": task_2.id, "authenticated_user": user_2}, [task_2_event]),
        ({"task_id": task_2.id, "authenticated_user": user_1}, []),
    ]

    for filters, expected_events in cases:
        with subtests.test():
            events = get_task_events(session=session, **filters)
            assert events == expected_events


def test_delete_task_event_ok(session):
    task_event = TaskEventFactory()

    delete_task_event(
        session=session,
        authenticated_user=task_event.task.user,
        task_event_id=task_event.id,
    )

    assert session.get(TaskEvent, task_event.id) is None


def test_delete_task_event_failure_not_visible_to_user(session):
    task_event = TaskEventFactory()

    with pytest.raises(NoResultFound) as ctx:
        delete_task_event(
            session=session,
            authenticated_user=UserFactory(),
            task_event_id=task_event.id,
        )

    assert ctx.value.args[0] == "Task Event not found"
