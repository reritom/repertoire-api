import pytest
from sqlalchemy.exc import NoResultFound

from app.accounts.tests.factories import UserFactory
from app.tasks.models.task import TaskStatus
from app.tasks.services import task_service
from app.tasks.tests.factories import TaskFactory


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


def test_pause_task_ok(session):
    task = TaskFactory(status=TaskStatus.ongoing)

    task_service.pause_task(
        authenticated_user=task.user,
        task_id=task.id,
        session=session,
    )


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
