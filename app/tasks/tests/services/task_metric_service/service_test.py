import pytest
from sqlalchemy.exc import NoResultFound

from app.accounts.tests.factories import UserFactory
from app.shared.exceptions import ServiceValidationError
from app.tasks.models.task_metric import TaskMetric
from app.tasks.schemas.task_metric_schema import TaskMetricCreationSchema
from app.tasks.services.task_metric_service.service import (
    create_task_metric,
    delete_task_metric,
    get_task_metric,
    get_task_metrics,
)
from app.tasks.tests.factories import TaskFactory, TaskMetricFactory


def test_create_task_metric_ok(session):
    user = UserFactory()

    # Noise
    TaskMetricFactory(name="myname")  # with same name but under a different user
    TaskMetricFactory(
        name="myname", task__user=user
    )  # with same name but under a different task

    task = TaskFactory(user=user)

    task_metric = create_task_metric(
        session=session,
        authenticated_user=user,
        task_metric_creation_payload=TaskMetricCreationSchema(
            task_id=task.id,
            name="myname",
            prompt="myprompt",
            required=True,
        ),
    )

    assert task_metric.task == task
    assert task_metric.name == "myname"
    assert task_metric.prompt == "myprompt"
    assert task_metric.required is True


def test_create_task_metric_failure_duplicate_name(session):
    user = UserFactory()
    task = TaskFactory(user=user)
    TaskMetricFactory(task=task, name="myname")

    with pytest.raises(ServiceValidationError) as ctx:
        create_task_metric(
            session=session,
            authenticated_user=user,
            task_metric_creation_payload=TaskMetricCreationSchema(
                task_id=task.id,
                name="myname",
                prompt="myprompt",
                required=True,
            ),
        )

    assert ctx.value.args[0] == "A metric already exists with this name for this task"


def test_create_task_metric_failure_task_not_visible_to_user(session):
    user = UserFactory()
    task = TaskFactory()

    with pytest.raises(NoResultFound) as ctx:
        create_task_metric(
            session=session,
            authenticated_user=user,
            task_metric_creation_payload=TaskMetricCreationSchema(
                task_id=task.id,
                name="myname",
                prompt="myprompt",
                required=True,
            ),
        )

    assert ctx.value.args[0] == "Task not found"


def test_get_task_metric_ok(session):
    task_metric = TaskMetricFactory()

    retrieved = get_task_metric(
        session=session,
        authenticated_user=task_metric.task.user,
        task_metric_id=task_metric.id,
    )

    assert retrieved == task_metric


def test_get_task_metric_failure_not_visible_to_user(session):
    task_metric = TaskMetricFactory()

    with pytest.raises(NoResultFound) as ctx:
        get_task_metric(
            session=session,
            authenticated_user=UserFactory(),
            task_metric_id=task_metric.id,
        )

    assert ctx.value.args[0] == "Task Metric not found"


def test_get_task_metrics_ok(session, subtests):
    user_1 = UserFactory()
    task_1 = TaskFactory(user=user_1)
    task_1_metric = TaskMetricFactory(task=task_1)

    user_2 = UserFactory()
    task_2 = TaskFactory(user=user_2)
    task_2_metric = TaskMetricFactory(task=task_2)

    cases = [
        ({"task_id": task_1.id, "authenticated_user": user_1}, [task_1_metric]),
        ({"task_id": task_2.id, "authenticated_user": user_2}, [task_2_metric]),
        ({"task_id": task_2.id, "authenticated_user": user_1}, []),
    ]

    for filters, expected_metrics in cases:
        with subtests.test():
            metrics = get_task_metrics(session=session, **filters)
            assert metrics == expected_metrics


def test_delete_task_metric_ok(session):
    task_metric = TaskMetricFactory()

    delete_task_metric(
        session=session,
        authenticated_user=task_metric.task.user,
        task_metric_id=task_metric.id,
    )

    assert session.get(TaskMetric, task_metric.id) is None


def test_delete_task_metric_failure_not_visible_to_user(session):
    task_metric = TaskMetricFactory()

    with pytest.raises(NoResultFound) as ctx:
        delete_task_metric(
            session=session,
            authenticated_user=UserFactory(),
            task_metric_id=task_metric.id,
        )

    assert ctx.value.args[0] == "Task Metric not found"
