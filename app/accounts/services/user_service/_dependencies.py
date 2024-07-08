from fast_depends import Depends

from app.accounts.daos.user_dao import UserDao
from app.accounts.models.user import User
from app.database import SessionType


def get_user_dao(session: SessionType) -> UserDao:
    return UserDao(session=session)


def get_user(user_id: int, user_dao: UserDao = Depends(get_user_dao)) -> User:
    return user_dao.get(id=user_id)
