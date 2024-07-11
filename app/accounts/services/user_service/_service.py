from fast_depends import Depends, inject

from app.accounts.daos.user_dao import UserDao
from app.accounts.models.user import User
from app.accounts.schemas.user_schema import UserCreationSchema
from app.accounts.services.user_service._dependencies import get_user_dao
from app.accounts.services.user_service._utils import check_password, hash_password
from app.database import SessionType
from app.shared.exceptions import ServiceValidationError


@inject
def _create_user(
    session: SessionType,
    user_creation_payload: UserCreationSchema,
    # Injected
    user_dao: UserDao = Depends(get_user_dao),
) -> User:
    # TODO validate email is unique (and/or catch the integrity error)
    user = user_dao.create(
        email=user_creation_payload.email,
        password_hash=hash_password(user_creation_payload.password),
    )
    session.commit()
    return user


@inject
def _get_user_from_credentials(
    email: str,
    password: str,
    # Injected
    user_dao: UserDao = Depends(get_user_dao),
) -> User:
    user = user_dao.get(email=email, raise_exc=False)
    if user and check_password(password, hashed_password=user.password_hash):
        return user

    raise ServiceValidationError("Invalid credentials")


@inject
def _get_user(
    user_id: int,
    # Injected
    user_dao: UserDao = Depends(get_user_dao),
) -> User:
    return user_dao.get(id=user_id)
