from datetime import datetime
from typing import Optional, Tuple


from app.accounts.models.user import User
from app.auth.schemas.login_schema import LoginSchema
from app.database import SessionType

from ._service import _get_authenticated_user, _login_user


def login_user(
    session: SessionType,
    user_credentials: LoginSchema,
) -> Tuple[str, datetime]:
    return _login_user(
        session=session,
        user_credentials=user_credentials,
    )


def get_authenticated_user(
    session: SessionType,
    access_token: str,
) -> Optional[User]:
    return _get_authenticated_user(
        session=session,
        access_token=access_token,
    )
