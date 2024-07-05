import pytest
from sqlalchemy.exc import NoResultFound

from app.accounts.tests.factories import UserFactory
from app.shared.exceptions import ServiceValidationError
from app.tasks.models.task_event_metric import TaskEventMetric
from app.tasks.schemas.task_event_metric_schema import TaskEventMetricCreationSchema
from app.tasks.services.task_event_metric_service.service import (
    create_task_event_metric,
    delete_task_event_metric,
    get_task_event_metric,
    get_task_event_metrics,
)
from app.tasks.tests.factories import (
    TaskEventFactory,
    TaskEventMetricFactory,
    TaskFactory,
    TaskMetricFactory,
)


def test_create_task_event_metric_ok(session):
    # Noise
    UserFactory.create_batch(1)
    TaskFactory.create_batch(2)
    TaskEventFactory.create_batch(3)
    TaskMetricFactory.create_batch(4)
    TaskEventMetricFactory.create_batch(5)

    user = UserFactory()
    task = TaskFactory(user=user)
    event = TaskEventFactory(task=task)
    metric = TaskMetricFactory(task=task)

    event_metric = create_task_event_metric(
        session=session,
        authenticated_user=user,
        task_event_metric_creation_payload=TaskEventMetricCreationSchema(
            task_event_id=event.id,
            task_metric_id=metric.id,
            value=10,
        ),
    )

    assert event_metric.task_event == event
    assert event_metric.task_metric == metric
    assert event_metric.value == 10


def test_create_task_event_metric_failure_task_event_not_visible_to_user(session):
    user = UserFactory()
    task = TaskFactory(user=user)
    event = TaskEventFactory()
    metric = TaskMetricFactory(task=task)

    with pytest.raises(NoResultFound) as ctx:
        create_task_event_metric(
            session=session,
            authenticated_user=user,
            task_event_metric_creation_payload=TaskEventMetricCreationSchema(
                task_event_id=event.id,
                task_metric_id=metric.id,
                value=10,
            ),
        )

    assert ctx.value.args[0] == "Task Event not found"


def test_create_task_event_metric_failure_task_metric_not_visible_to_user(session):
    user = UserFactory()
    task = TaskFactory(user=user)
    event = TaskEventFactory(task=task)
    metric = TaskMetricFactory()

    with pytest.raises(NoResultFound) as ctx:
        create_task_event_metric(
            session=session,
            authenticated_user=user,
            task_event_metric_creation_payload=TaskEventMetricCreationSchema(
                task_event_id=event.id,
                task_metric_id=metric.id,
                value=10,
            ),
        )

    assert ctx.value.args[0] == "Task Metric not found"


def test_create_task_event_metric_failure_duplicate(session):
    user = UserFactory()
    task = TaskFactory(user=user)
    existing = TaskEventMetricFactory(task=task)

    with pytest.raises(ServiceValidationError) as ctx:
        create_task_event_metric(
            session=session,
            authenticated_user=user,
            task_event_metric_creation_payload=TaskEventMetricCreationSchema(
                task_event_id=existing.task_event_id,
                task_metric_id=existing.task_metric_id,
                value=10,
            ),
        )

    assert ctx.value.args[0] == "A metric value has already been applied"


def test_create_task_event_metric_failure_task_not_the_same(session):
    user = UserFactory()
    event = TaskEventFactory(task__user=user)
    metric = TaskMetricFactory(task__user=user)

    with pytest.raises(ServiceValidationError) as ctx:
        create_task_event_metric(
            session=session,
            authenticated_user=user,
            task_event_metric_creation_payload=TaskEventMetricCreationSchema(
                task_event_id=event.id,
                task_metric_id=metric.id,
                value=10,
            ),
        )

    assert ctx.value.args[0] == "Task metric and event aren't related to the same task"


def test_get_task_event_metric_ok(session):
    task_event_metric = TaskEventMetricFactory()

    retrieved = get_task_event_metric(
        session=session,
        authenticated_user=task_event_metric.task_event.task.user,
        task_event_metric_id=task_event_metric.id,
    )

    assert retrieved == task_event_metric


def test_get_task_event_metric_failure_not_visible_to_user(session):
    task_event_metric = TaskEventMetricFactory()

    with pytest.raises(NoResultFound) as ctx:
        get_task_event_metric(
            session=session,
            authenticated_user=UserFactory(),
            task_event_metric_id=task_event_metric.id,
        )

    assert ctx.value.args[0] == "Task Event Metric not found"


def test_get_task_event_metrics(session, subtests):
    user_1 = UserFactory()
    user_1_event_metric_1 = TaskEventMetricFactory(task__user=user_1)
    user_1_event_metric_2 = TaskEventMetricFactory(task__user=user_1)

    user_2 = UserFactory()
    user_2_event_metric_1 = TaskEventMetricFactory(task__user=user_2)

    cases = [
        # User 1 can see their event metrics with no filters
        ({}, user_1, [user_1_event_metric_1, user_1_event_metric_2]),
        # User 1 can see the event metric of a specific metric of theirs
        (
            {"task_metric_id": user_1_event_metric_1.task_metric_id},
            user_1,
            [user_1_event_metric_1],
        ),
        # User 1 can see the event metric of a specific event of theirs
        (
            {"task_event_id": user_1_event_metric_2.task_event_id},
            user_1,
            [user_1_event_metric_2],
        ),
        # User 2 cannot see the event metric of a specific event that isn't theirs
        (
            {"task_event_id": user_1_event_metric_2.task_event_id},
            user_2,
            [],
        ),
        # User 2 can see their event metrics with no filters
        ({}, user_2, [user_2_event_metric_1]),
    ]

    for filters, authenticated_user, expected_task_event_metrics in cases:
        with subtests.test():
            task_event_metrics = get_task_event_metrics(
                session=session,
                authenticated_user=authenticated_user,
                **filters,
            )
            assert task_event_metrics == expected_task_event_metrics


def test_delete_task_event_metric_ok(session):
    task_event_metric = TaskEventMetricFactory()

    delete_task_event_metric(
        session=session,
        authenticated_user=task_event_metric.task_event.task.user,
        task_event_metric_id=task_event_metric.id,
    )

    assert session.get(TaskEventMetric, task_event_metric.id) is None


def test_delete_task_event_metric_failure_not_visible_to_user(session):
    task_event_metric = TaskEventMetricFactory()

    with pytest.raises(NoResultFound) as ctx:
        delete_task_event_metric(
            session=session,
            authenticated_user=UserFactory(),
            task_event_metric_id=task_event_metric.id,
        )

    assert ctx.value.args[0] == "Task Event Metric not found"
