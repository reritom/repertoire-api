from fast_depends import Depends

from app.database import SessionType
from app.tasks.daos.category_dao import CategoryDao


def get_category_dao(session: SessionType = Depends):
    return CategoryDao(session=session)
