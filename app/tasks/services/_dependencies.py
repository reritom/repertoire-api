from fast_depends import Depends

from app.database import SessionType
from app.tasks.daos.category_dao import CategoryDao
from app.tasks.daos.task_dao import TaskDao


def get_category_dao(session: SessionType = Depends):
    return CategoryDao(session=session)


def get_task_dao(session: SessionType = Depends):
    return TaskDao(session=session)
