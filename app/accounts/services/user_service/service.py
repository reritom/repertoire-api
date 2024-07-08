from app.accounts.models.user import User
from app.accounts.schemas.user_schema import UserCreationSchema
from app.database import SessionType

from ._service import _create_user, _get_user, _validate_credentials


def create_user(
    session: SessionType,
    user_creation_payload: UserCreationSchema,
) -> User:
    return _create_user(
        session=session,
        user_creation_payload=user_creation_payload,
    )


def validate_credentials(
    user_id: int,
    password: str,
) -> bool:
    return _validate_credentials(user_id=user_id, password=password)


def get_user(session: SessionType, user_id: int) -> User:
    return _get_user(session=session, user_id=user_id)
