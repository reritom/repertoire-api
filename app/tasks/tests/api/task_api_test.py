from datetime import date

from fastapi.testclient import TestClient

from app.accounts.tests.factories import UserFactory
from app.tasks.models.task import Task, TaskStatus
from app.tasks.models.task_frequency import FrequencyPeriod, FrequencyType
from app.tasks.models.task_until import UntilType
from app.tasks.tests.factories import TaskFactory


def test_create_task_failure_not_authenticated(client: TestClient):
    response = client.post("/api/tasks", json={})

    assert response.status_code == 401
    assert response.json() == {"detail": "Authentication required"}


def test_create_task_failure_missing_fields(client: TestClient, using_user):
    with using_user(UserFactory()):
        response = client.post("/api/tasks", json={})

    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {"type": "missing", "loc": ["body", "name"], "msg": "Field required"},
            {
                "type": "missing",
                "loc": ["body", "description"],
                "msg": "Field required",
            },
            {"type": "missing", "loc": ["body", "frequency"], "msg": "Field required"},
            {"type": "missing", "loc": ["body", "until"], "msg": "Field required"},
        ]
    }


def test_create_task_failure_duplicate_name(client: TestClient, using_user):
    user = UserFactory()
    TaskFactory(user=user, name="myname")

    with using_user(user):
        response = client.post(
            "/api/tasks",
            json={
                "name": "myname",
                "description": "mydesc",
                "frequency": {"type": "per", "period": "week", "amount": "2"},
                "until": {"type": "amount", "amount": 5},
            },
        )

    assert response.status_code == 400
    assert response.json() == {
        "message": "A task already exists with this name",
        "type": "ServiceValidationError",
    }


def test_create_task_failure_missing_conditional_field(client: TestClient, using_user):
    user = UserFactory()

    with using_user(user):
        response = client.post(
            "/api/tasks",
            json={
                "name": "myname",
                "description": "mydesc",
                "frequency": {"type": "per", "period": "week", "amount": "2"},
                "until": {"type": "date"},  # Date field required
            },
        )

    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "type": "expected_conditional_field",
                "loc": ["body", "until"],
                "msg": "Until date must be set",
            }
        ]
    }


def test_create_task_ok(client: TestClient, using_user):
    TaskFactory(name="myname")  # Noise

    user = UserFactory()

    with using_user(user):
        response = client.post(
            "/api/tasks",
            json={
                "name": "myname",
                "description": "mydesc",
                "frequency": {"type": "per", "period": "week", "amount": "2"},
                "until": {"type": "amount", "amount": 5},
            },
        )

    assert response.status_code == 201
    response_json = response.json()
    assert response_json == {
        "name": "myname",
        "description": "mydesc",
        "category_id": None,
        "frequency": {
            "type": "per",
            "period": "week",
            "amount": 2,
            "use_calendar_period": True,
            "once_on_date": None,
            "once_per_weekday": None,
            "once_at_time": None,
        },
        "until": {"type": "amount", "amount": 5, "date": None},
        "id": response_json["id"],
        "created": response_json["created"],
        "next_event_datetime": response_json["next_event_datetime"],
    }


def test_get_tasks_failure_not_authenticated(client: TestClient):
    response = client.get("/api/tasks")

    assert response.status_code == 401
    assert response.json() == {"detail": "Authentication required"}


def test_get_tasks_ok(client: TestClient, using_user):
    TaskFactory()  # Noise

    user = UserFactory()
    task = TaskFactory(user=user)

    with using_user(user):
        response = client.get("/api/tasks")

    assert response.status_code == 200
    assert response.json() == [
        {
            "name": task.name,
            "description": task.description,
            "category_id": task.category_id,
            "frequency": {
                "type": task.frequency.type.value,
                "period": task.frequency.period.value,
                "amount": task.frequency.amount,
                "use_calendar_period": task.frequency.use_calendar_period,
                "once_on_date": task.frequency.once_on_date,
                "once_per_weekday": task.frequency.once_per_weekday,
                "once_at_time": task.frequency.once_at_time,
            },
            "until": {
                "type": task.until.type.value,
                "amount": task.until.amount,
                "date": task.until.date,
            },
            "id": task.id,
            "created": task.created.strftime("%Y-%m-%dT%H:%M:%S"),
            "next_event_datetime": task.next_event_datetime,
        }
    ]


# TODO test filters


def test_get_task_failure_not_authenticated(client: TestClient):
    response = client.get("/api/tasks/12345")

    assert response.status_code == 401
    assert response.json() == {"detail": "Authentication required"}


def test_get_task_failure_not_visible_to_user(client: TestClient, using_user):
    task = TaskFactory()

    with using_user(UserFactory()):
        response = client.get(f"/api/tasks/{task.id}")

    assert response.status_code == 404
    assert response.json() == {"message": "Task not found", "type": "NoResultFound"}


def test_get_task_ok(client: TestClient, using_user):
    user = UserFactory()
    task = TaskFactory(user=user)

    with using_user(user):
        response = client.get(f"/api/tasks/{task.id}")

    assert response.status_code == 200
    assert response.json() == {
        "name": task.name,
        "description": task.description,
        "category_id": task.category_id,
        "frequency": {
            "type": task.frequency.type.value,
            "period": task.frequency.period.value,
            "amount": task.frequency.amount,
            "use_calendar_period": task.frequency.use_calendar_period,
            "once_on_date": task.frequency.once_on_date,
            "once_per_weekday": task.frequency.once_per_weekday,
            "once_at_time": task.frequency.once_at_time,
        },
        "until": {
            "type": task.until.type.value,
            "amount": task.until.amount,
            "date": task.until.date,
        },
        "id": task.id,
        "created": task.created.strftime("%Y-%m-%dT%H:%M:%S"),
        "next_event_datetime": task.next_event_datetime,
    }


def test_delete_task_failure_not_authenticated(client: TestClient):
    response = client.delete("/api/tasks/12345")

    assert response.status_code == 401
    assert response.json() == {"detail": "Authentication required"}


def test_delete_task_failure_not_visible_to_user(client: TestClient, using_user):
    task = TaskFactory()

    with using_user(UserFactory()):
        response = client.delete(f"/api/tasks/{task.id}")

    assert response.status_code == 404
    assert response.json() == {"message": "Task not found", "type": "NoResultFound"}


def test_delete_task_ok(client: TestClient, using_user, session):
    user = UserFactory()
    task = TaskFactory(user=user)

    with using_user(user):
        response = client.delete(f"/api/tasks/{task.id}")

    assert response.status_code == 204
    assert session.get(Task, task.id) is None


def test_pause_task_failure_not_authenticated(client: TestClient):
    response = client.post("/api/tasks/12345/pause")

    assert response.status_code == 401
    assert response.json() == {"detail": "Authentication required"}


def test_pause_task_failure_task_not_visible_to_user(client: TestClient, using_user):
    task = TaskFactory()

    with using_user(UserFactory()):
        response = client.post(f"/api/tasks/{task.id}/pause")

    assert response.status_code == 404
    assert response.json() == {"message": "Task not found", "type": "NoResultFound"}


def test_pause_task_failure_task_not_ongoing(client: TestClient, using_user):
    user = UserFactory()
    task = TaskFactory(user=user, status=TaskStatus.paused)

    with using_user(user):
        response = client.post(f"/api/tasks/{task.id}/pause")

    assert response.status_code == 400
    assert response.json() == {
        "message": "Cannot pause a task that isn't ongoing",
        "type": "ServiceValidationError",
    }


def test_pause_task_ok(client: TestClient, using_user, session):
    user = UserFactory()
    task = TaskFactory(user=user, status=TaskStatus.ongoing)

    with using_user(user):
        response = client.post(f"/api/tasks/{task.id}/pause")

    assert response.status_code == 204
    session.refresh(task)
    assert task.status == TaskStatus.paused


def test_unpause_task_failure_not_authenticated(client: TestClient):
    response = client.post("/api/tasks/12345/unpause")

    assert response.status_code == 401
    assert response.json() == {"detail": "Authentication required"}


def test_unpause_task_failure_task_not_visible_to_user(client: TestClient, using_user):
    task = TaskFactory()

    with using_user(UserFactory()):
        response = client.post(f"/api/tasks/{task.id}/unpause")

    assert response.status_code == 404
    assert response.json() == {"message": "Task not found", "type": "NoResultFound"}


def test_unpause_task_failure_task_not_paused(client: TestClient, using_user):
    user = UserFactory()
    task = TaskFactory(user=user, status=TaskStatus.ongoing)

    with using_user(user):
        response = client.post(f"/api/tasks/{task.id}/unpause")

    assert response.status_code == 400
    assert response.json() == {
        "message": "Cannot unpause a task that isn't paused",
        "type": "ServiceValidationError",
    }


def test_unpause_task_ok(client: TestClient, using_user, session):
    user = UserFactory()
    task = TaskFactory(user=user, status=TaskStatus.paused)

    with using_user(user):
        response = client.post(f"/api/tasks/{task.id}/unpause")

    assert response.status_code == 204
    session.refresh(task)
    assert task.status == TaskStatus.ongoing


def test_complete_task_failure_not_authenticated(client: TestClient):
    response = client.post("/api/tasks/12345/complete")

    assert response.status_code == 401
    assert response.json() == {"detail": "Authentication required"}


def test_complete_task_failure_task_not_visible_to_user(client: TestClient, using_user):
    task = TaskFactory()

    with using_user(UserFactory()):
        response = client.post(f"/api/tasks/{task.id}/complete")

    assert response.status_code == 404
    assert response.json() == {"message": "Task not found", "type": "NoResultFound"}


def test_complete_task_failure_task_already_completed(client: TestClient, using_user):
    user = UserFactory()
    task = TaskFactory(user=user, status=TaskStatus.completed)

    with using_user(user):
        response = client.post(f"/api/tasks/{task.id}/complete")

    assert response.status_code == 400
    assert response.json() == {
        "message": "The task is already completed",
        "type": "ServiceValidationError",
    }


def test_complete_task_ok(client: TestClient, using_user, session):
    user = UserFactory()
    task = TaskFactory(user=user, status=TaskStatus.ongoing)

    with using_user(user):
        response = client.post(f"/api/tasks/{task.id}/complete")

    assert response.status_code == 204
    session.refresh(task)
    assert task.status == TaskStatus.completed


def test_update_task_frequency_failure_not_authenticated(client: TestClient):
    response = client.put("/api/tasks/12345/frequency", json={})

    assert response.status_code == 401
    assert response.json() == {"detail": "Authentication required"}


def test_update_task_frequency_failure_missing_fields(client: TestClient, using_user):
    with using_user(UserFactory()):
        response = client.put("/api/tasks/12345/frequency", json={})

    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {"type": "missing", "loc": ["body", "type"], "msg": "Field required"},
            {"type": "missing", "loc": ["body", "amount"], "msg": "Field required"},
        ]
    }


def test_update_task_frequency_failure_task_not_visible_to_user(
    client: TestClient, using_user
):
    task = TaskFactory()

    with using_user(UserFactory()):
        response = client.put(
            f"/api/tasks/{task.id}/frequency",
            json={"type": "per", "period": "month", "amount": 5},
        )

    assert response.status_code == 404
    assert response.json() == {"message": "Task not found", "type": "NoResultFound"}


def test_update_task_frequency_ok(client: TestClient, using_user, session):
    user = UserFactory()
    task = TaskFactory(
        user=user,
        frequency__amount=1,
        frequency__type=FrequencyType.on,
        frequency__period=FrequencyPeriod.day,
    )

    with using_user(user):
        response = client.put(
            f"/api/tasks/{task.id}/frequency",
            json={"type": "per", "period": "month", "amount": 5},
        )

    assert response.status_code == 204
    session.refresh(task)
    assert task.frequency.period == FrequencyPeriod.month
    assert task.frequency.type == FrequencyType.per
    assert task.frequency.amount == 5


def test_update_task_until_failure_not_authenticated(client: TestClient):
    response = client.put("/api/tasks/12345/until", json={})

    assert response.status_code == 401
    assert response.json() == {"detail": "Authentication required"}


def test_update_task_until_failure_missing_fields(client: TestClient, using_user):
    with using_user(UserFactory()):
        response = client.put("/api/tasks/12345/until", json={})

    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {"type": "missing", "loc": ["body", "type"], "msg": "Field required"}
        ]
    }


def test_update_task_until_failure_task_not_visible_to_user(
    client: TestClient, using_user
):
    task = TaskFactory()

    with using_user(UserFactory()):
        response = client.put(
            f"/api/tasks/{task.id}/until",
            json={"type": "amount", "amount": 4},
        )

    assert response.status_code == 404
    assert response.json() == {"message": "Task not found", "type": "NoResultFound"}


def test_update_task_until_ok(client: TestClient, using_user, session):
    user = UserFactory()
    task = TaskFactory(
        user=user,
        until__type=UntilType.date,
        until__date=date(2025, 12, 25),
        until__amount=None,
    )

    with using_user(user):
        response = client.put(
            f"/api/tasks/{task.id}/until",
            json={"type": "amount", "amount": 4},
        )

    assert response.status_code == 204
    session.refresh(task)
    assert task.until.type == UntilType.amount
    assert task.until.date is None
    assert task.until.amount == 4
