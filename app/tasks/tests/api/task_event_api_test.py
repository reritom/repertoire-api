from fastapi.testclient import TestClient

from app.accounts.tests.factories import UserFactory
from app.tasks.models.task_event import TaskEvent
from app.tasks.tests.factories import TaskEventFactory, TaskFactory


def test_create_task_event_failure_not_authenticated(client: TestClient):
    response = client.post("/api/task-events", json={})

    assert response.status_code == 401
    assert response.json() == {"detail": "Authentication required"}


def test_create_task_event_failure_missing_fields(client: TestClient, using_user):
    with using_user(UserFactory()):
        response = client.post("/api/task-events", json={})

    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {"type": "missing", "loc": ["body", "task_id"], "msg": "Field required"},
            {"type": "missing", "loc": ["body", "around"], "msg": "Field required"},
        ]
    }


def test_create_task_event_failure_task_not_visible_to_user(
    client: TestClient, using_user
):
    task = TaskFactory()

    with using_user(UserFactory()):
        response = client.post(
            "/api/task-events",
            json={
                "task_id": task.id,
                "around": "today",
            },
        )

    # TODO this should maybe be a 400 service validation error
    assert response.status_code == 404
    assert response.json() == {
        "message": "Task not found",
        "type": "NoResultFound",
    }


def test_create_task_event_ok(client: TestClient, using_user):
    user = UserFactory()
    task = TaskFactory(user=user)

    with using_user(user):
        response = client.post(
            "/api/task-events",
            json={
                "task_id": task.id,
                "around": "today",
            },
        )

    assert response.status_code == 201
    response_json = response.json()
    assert response_json == {
        "task_id": task.id,
        "around": "today",
        "at": None,
        "effective_datetime": response_json["effective_datetime"],
        "created": response_json["created"],
        "id": response_json["id"],
    }


def test_get_task_events_failure_not_authenticated(client: TestClient):
    response = client.get("/api/task-events")

    assert response.status_code == 401
    assert response.json() == {"detail": "Authentication required"}


def test_get_task_events_failure_missing_required_filter(
    client: TestClient, using_user
):
    with using_user(UserFactory()):
        response = client.get("/api/task-events")

    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {"type": "missing", "loc": ["query", "task_id"], "msg": "Field required"}
        ]
    }


def test_get_task_events_ok(client: TestClient, using_user):
    user = UserFactory()
    TaskEventFactory(task__user=user)  # Noise
    task_event = TaskEventFactory(task__user=user)

    with using_user(user):
        response = client.get(
            "/api/task-events", params={"task_id": task_event.task_id}
        )

    assert response.status_code == 200
    assert response.json() == [
        {
            "task_id": task_event.task_id,
            "around": task_event.around.value,
            "at": task_event.at,
            "effective_datetime": task_event.effective_datetime.strftime(
                "%Y-%m-%dT%H:%M:%S"
            ),
            "created": task_event.created.strftime("%Y-%m-%dT%H:%M:%S"),
            "id": task_event.id,
        }
    ]


def test_get_task_event_failure_not_authenticated(client: TestClient):
    response = client.get("/api/task-events/12345")

    assert response.status_code == 401
    assert response.json() == {"detail": "Authentication required"}


def test_get_task_event_failure_not_visible_to_user(client: TestClient, using_user):
    task_event = TaskEventFactory()

    with using_user(UserFactory()):
        response = client.get(f"/api/task-events/{task_event.id}")

    assert response.status_code == 404
    assert response.json() == {
        "message": "Task Event not found",
        "type": "NoResultFound",
    }


def test_get_task_event_ok(client: TestClient, using_user):
    user = UserFactory()
    task_event = TaskEventFactory(task__user=user)

    with using_user(user):
        response = client.get(f"/api/task-events/{task_event.id}")

    assert response.status_code == 200
    assert response.json() == {
        "task_id": task_event.task_id,
        "around": task_event.around.value,
        "at": task_event.at,
        "effective_datetime": task_event.effective_datetime.strftime(
            "%Y-%m-%dT%H:%M:%S"
        ),
        "created": task_event.created.strftime("%Y-%m-%dT%H:%M:%S"),
        "id": task_event.id,
    }


def test_delete_task_event_failure_not_authenticated(client: TestClient):
    response = client.delete("/api/task-events/12345")

    assert response.status_code == 401
    assert response.json() == {"detail": "Authentication required"}


def test_delete_task_event_failure_not_visible_to_user(client: TestClient, using_user):
    task_event = TaskEventFactory()

    with using_user(UserFactory()):
        response = client.delete(f"/api/task-events/{task_event.id}")

    assert response.status_code == 404
    assert response.json() == {
        "message": "Task Event not found",
        "type": "NoResultFound",
    }


def test_delete_task_event_ok(client: TestClient, using_user, session):
    user = UserFactory()
    task_event = TaskEventFactory(task__user=user)

    with using_user(user):
        response = client.delete(f"/api/task-events/{task_event.id}")

    assert response.status_code == 204
    assert session.get(TaskEvent, task_event.id) is None
