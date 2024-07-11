from datetime import datetime, timedelta
from typing import Optional, Tuple

from fast_depends import Depends, inject

from app.accounts.models.user import User
from app.accounts.services.user_service.service import (
    get_user,
    get_user_from_credentials,
)
from app.auth.schemas.login_schema import LoginSchema
from app.auth.services.auth_service._dependencies import (
    get_access_token_lifespan_minutes,
    get_authentication_secret_key,
)
from app.database import SessionType

from ._utils import create_access_token, decode_access_token


@inject
def _login_user(
    session: SessionType,
    user_credentials: LoginSchema,
    # Injected
    secret_key: str = Depends(get_authentication_secret_key),
    access_token_lifespan_minutes: int = Depends(get_access_token_lifespan_minutes),
) -> Tuple[str, datetime]:
    user = get_user_from_credentials(
        session=session,
        email=user_credentials.email,
        password=user_credentials.password,
    )
    expiration_datetime = datetime.utcnow() + timedelta(
        minutes=access_token_lifespan_minutes
    )
    token = create_access_token(
        expires=expiration_datetime,
        secret_key=secret_key,
        user_id=user.id,
    )
    return token, expiration_datetime


@inject
def _get_authenticated_user(
    session: SessionType,
    access_token: str,
    # Injected
    secret_key: str = Depends(get_authentication_secret_key),
) -> Optional[User]:
    payload = decode_access_token(
        token=access_token, secret_key=secret_key, raise_exc=False
    )

    if payload:
        return get_user(session=session, user_id=payload["sub"])
