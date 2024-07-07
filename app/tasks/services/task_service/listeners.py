from app.accounts.models.user import User
from app.database import SessionType
from app.tasks.services.task_event_service.signals import (
    task_event_created,
    task_event_deleted,
)
from app.tasks.services.task_service.service import (
    recompute_task_state,
)
from app.tasks.services.task_service.signals import task_updated


@task_updated.connect
@task_event_created.connect
@task_event_deleted.connect
def trigger_task_state_recompute(
    sender,
    task_id: int,
    session: SessionType,
    authenticated_user: User,
):
    recompute_task_state(
        session=session,
        authenticated_user=authenticated_user,
        task_id=task_id,
    )
