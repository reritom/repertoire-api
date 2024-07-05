from app.accounts.models.user import User
from app.database import SessionType
from app.tasks.services.task_event_service.signals import (
    task_event_created,
    task_event_deleted,
)
from app.tasks.services.task_service.service import recompute_task_status


@task_event_created.connect
@task_event_deleted.connect
def trigger_task_status_recompute(
    sender,
    task_id: int,
    session: SessionType,
    authenticated_user: User,
):
    print("Triggering recompute")
    recompute_task_status(
        session=session,
        authenticated_user=authenticated_user,
        task_id=task_id,
    )
