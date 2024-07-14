from typing import Annotated, Optional

from fastapi import Depends
from fastapi.exceptions import HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.accounts.models.user import User
from app.auth.services.auth_service.service import (
    get_authenticated_user as _get_authenticated_user,
)
from app.database import SessionType, get_session

security = HTTPBearer(auto_error=False)


def get_authenticated_user(
    credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(security)],
    session: SessionType = Depends(get_session),
) -> Optional[User]:
    if credentials:
        return _get_authenticated_user(
            session=session, access_token=credentials.credentials
        )


def authenticated_user_required(
    authenticated_user: Optional[User] = Depends(get_authenticated_user),
) -> None:
    if not authenticated_user:
        raise HTTPException(status_code=401, detail="Authenticated required")


def unauthenticated_user_required(
    authenticated_user: Optional[User] = Depends(get_authenticated_user),
) -> None:
    if authenticated_user:
        raise HTTPException(status_code=403, detail="Already authenticated")
