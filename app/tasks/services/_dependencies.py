from typing import Callable

from fast_depends import Depends

from app.accounts.models.user import User
from app.database import SessionType
from app.tasks.daos.category_dao import CategoryDao
from app.tasks.daos.task_dao import TaskDao


def get_category_dao(session: SessionType = Depends):
    return CategoryDao(session=session)


def get_task_dao(session: SessionType = Depends):
    return TaskDao(session=session)


def get_task(
    session: SessionType = Depends,
    authenticated_user: User = Depends,
    task_id: int = Depends,
):
    from app.tasks.services.task_service import service

    return service.get_task(
        session=session,
        authenticated_user=authenticated_user,
        task_id=task_id,
    )


def get_default_task_id(task_id: int = Depends) -> int:
    return task_id


def get_task_factory(task_id_getter: Callable = get_default_task_id):
    def get_task(
        session: SessionType = Depends,
        authenticated_user: User = Depends,
        task_id: int = Depends(task_id_getter),
    ):
        from app.tasks.services.task_service import service

        return service.get_task(
            session=session,
            authenticated_user=authenticated_user,
            task_id=task_id,
        )

    return get_task
