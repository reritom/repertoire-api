from typing import Optional

from app.accounts.models.user import User
from app.accounts.schemas.user_schema import UserCreationSchema
from app.database import SessionType

from ._service import _create_user, _get_user, _get_user_from_credentials


def create_user(
    session: SessionType,
    user_creation_payload: UserCreationSchema,
) -> User:
    return _create_user(
        session=session,
        user_creation_payload=user_creation_payload,
    )


def get_user_from_credentials(
    session: SessionType,
    email: str,
    password: str,
) -> Optional[User]:
    return _get_user_from_credentials(
        session=session,
        email=email,
        password=password,
    )


def get_user(session: SessionType, user_id: int) -> User:
    return _get_user(session=session, user_id=user_id)
