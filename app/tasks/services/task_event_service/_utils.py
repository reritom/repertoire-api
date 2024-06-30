from datetime import datetime, timedelta

from app.tasks.models.task_event import TaskEventAround
from app.tasks.schemas.task_event_schema import TaskEventCreationSchema


def compute_effective_datetime(
    task_event_creation_payload: TaskEventCreationSchema, created: datetime
):
    """Determine the exact or vague date of an event"""
    # TODO test this directly
    if task_event_creation_payload.around == TaskEventAround.today:
        return created

    if task_event_creation_payload.around == TaskEventAround.yesterday:
        return created - timedelta(days=1)

    return task_event_creation_payload.at
